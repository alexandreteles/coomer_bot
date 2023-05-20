import asyncio
import io
import uuid
from time import time

import aiohttp
import discord
import ujson
from loguru import logger as log
from toolz import filter

from config import *
from src.http_utils import *

cookies: dict[str, str] = load_cookies(cookie_jar_file)
model_cache: list[dict[str, str]] = []
last_model_cache_update: int = 0


async def get_id(data: list, name: str, service: str) -> str:
    """
    Returns the ID of a record for a given name and service in a list of dictionaries.

    Args:
        data (list): A list of dictionaries.
        name (str): The name to search for.
        service (str): The service to search for.

    Returns:
        str: The ID of the matching record, or None if not found.
    """

    matches = filter(
        lambda item: item.get("name") == name and item.get("service") == service, data
    )
    match = next(matches, None)

    return match.get("id") if match else None


async def get_models() -> list[dict[str, str]]:
    """Get a list of all models

    Returns:
        list[dict[str, str]]: JSON with all available models
    """
    global model_cache, last_model_cache_update
    if model_cache and last_model_cache_update > int(time()) - 60 * 60 * 1:  # 1 hour
        log.debug("Returning cached model list")
        return model_cache
    async with http_get(headers, cookies, models_url) as response:
        log.debug(f"Getting creators from {models_url}")
        await save_cookies(response.cookies, cookie_jar_file)
        model_cache = ujson.loads(await response.text())
        last_model_cache_update = int(time())
        return model_cache


async def get_model_info(
    model_id: str, service: str = "onlyfans"
) -> dict[str, str] | None:
    """Get info about a model

    Args:
        model_id (str): Model ID

    Returns:
        dict[str, str]: JSON with model info
    """
    log.debug(f"Getting info for model {model_id}")

    models = await get_models()

    if service == "fansly":
        model_id = await get_id(models, model_id, service)
        log.debug(f"Found model ID {model_id}")

    model_info = next(filter(lambda model: model["id"] == model_id, models), None)
    if model_info:
        log.debug(f"Found info for model {model_id}.")
    else:
        log.debug(f"Could not find info for model {model_id}.")
    return model_info


async def get_image_posts(
    service: str,
    model: str,
    offset: int,
    limit: int = 10,
) -> list[str]:
    """
    Returns a list of image URLs for a given model and offset.

    Args:
        model (str): The name of the model to retrieve images for.
        offset (int): The offset to use when scraping images.

    Returns:
        List[str]: A list of strings representing the URLs to the images found.
    """

    models = await get_models()

    if service == "fansly":
        model = await get_id(models, model, service)
        log.debug(f"Found model ID {model}")

    log.debug(f"Getting posts for {model} at offset {offset} with limit {limit}")
    async with http_get(
        headers, cookies, f"{user_base_url}/{service}/user/{model}?o={offset}"
    ) as response:
        await save_cookies(response.cookies, cookie_jar_file)
        posts: dict = ujson.loads(await response.text())
    links: list[str] = []
    for post in posts:
        for att in post["attachments"]:
            links.append(att["path"])
        if post["file"]:
            links.append(post["file"]["path"])
    return [f"{base_coomer}{link}" for link in links if link.endswith(".jpg")][:limit]


async def prepare_images(images: list[str]) -> list[discord.File]:
    """
    Converts a list of image URLs into a list of `discord.File` objects.

    Args:
        images (list): A list of strings representing URLs to the images.

    Returns:
        list[discord.File]: A list of `discord.File` objects, ready to be uploaded.
    """

    log.debug(f"Preparing images for upload...")
    client = aiohttp.ClientSession(headers=headers, cookies=cookies)

    async def process(image: str) -> discord.File | None:
        async with http_get(headers, cookies, image) as response:
            content: io.BytesIO = io.BytesIO(await response.read())

        image_size: int = content.getbuffer().nbytes
        if image_size > 1000 and image_size < 25000000:
            file_id = str(uuid.uuid4())
            file = discord.File(content, filename=f'{file_id}.{image.split(".")[-1]}')
            return file
        else:
            log.warning(f"Image {image} is too large or too small. Skipping.")
            return None

    image_objects: list[discord.File | None] = await asyncio.gather(
        *[process(image) for image in images]
    )

    await client.close()
    return list(filter(None, image_objects))
