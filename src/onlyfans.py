import asyncio
import io
import uuid
from itertools import chain

import aiohttp
import discord
import ujson
from loguru import logger as log
from time import time

from config import *
from src.http_utils import *

cookies: dict[str, str] = load_cookies(cookie_jar_file)
model_cache: list[dict[str, str]] = []
last_model_cache_update: int = 0


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


async def get_model_info(model_id: str) -> dict[str, str] | None:
    """Get info about a model

    Args:
        model_id (str): Model ID

    Returns:
        dict[str, str]: JSON with model info
    """
    log.debug(f"Getting info for model {model_id}")
    model_info = next(
        (model for model in await get_models() if model["id"] == model_id), None
    )
    if model_info:
        log.debug(f"Found info for model {model_id}.")
    else:
        log.debug(f"Could not find info for model {model_id}.")
    return model_info


async def get_image_posts(model: str, offset: int, limit: int = 10) -> list[str]:
    log.debug(f"Getting posts for {model} at offset {offset} with limit {limit}")
    async with http_get(
        headers, cookies, f"{user_base_url}/{model}?o={offset}"
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
    log.debug(f"Preparing images for upload...")
    client = aiohttp.ClientSession(headers=headers, cookies=cookies)

    async def process(image: str) -> discord.File | None:
        async with client.get(image) as response:
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
