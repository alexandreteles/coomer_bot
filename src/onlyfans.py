import asyncio
import io
import uuid
from itertools import chain

import aiohttp
import discord
import ujson
from bs4 import BeautifulSoup
from loguru import logger as log
from time import time

from config import *
from src.cookie_utils import *

cookies: dict[str, str] = load_cookies(cookie_jar_file)
model_cache: list[dict[str, str]] = []
last_model_cache_update: int = 0

async def get_models() -> list[dict[str, str]]:
    """Get a list of all creators

    Returns:
        list[dict[str, str]]: JSON with all available models
    """
    global model_cache, last_model_cache_update
    if model_cache and last_model_cache_update > int(time()) - 60 * 60 * 1: # 1 hour
        log.info("Returning cached model list")
        return model_cache
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as client:
        async with client.get(models_url) as response:
            log.info(f"Getting creators from {models_url}")
            await save_cookies(response.cookies, cookie_jar_file)
            model_cache = ujson.loads(await response.text())
            last_model_cache_update = int(time())
            return model_cache


async def get_model_info(model_id: str) -> dict[str, str] | None:
    """Get info about a creator

    Args:
        creator_id (str): Creator ID

    Returns:
        dict[str, str]: JSON with creator info
    """
    log.info(f"Getting info for creator {model_id}")
    creator_info: list[dict[str, str]] = [
        creator for creator in await get_models() if creator["id"] == model_id
    ]
    if creator_info:
        log.info(f"Found info for creator {model_id}. Returning results.")
        return creator_info[0]
    log.info(f"Could not find info for creator {model_id}.")
    return None


async def get_model_posts_offsets(model: str) -> list[int]:
    log.info(f"Getting offsets for {model} posts")
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as client:
        async with client.get(f"{user_base_url}/{model}") as response:
            log.info(f"Getting  data for {model} posts")
            await save_cookies(response.cookies, cookie_jar_file)
            soup = BeautifulSoup(await response.text(), "lxml")
    if soup.find("title").text.strip() != "Coomer":
        paginator: str = (
            soup.find("div", class_="paginator", id="paginator-top").findChild("small").text
        )
        posts: int = int(paginator.split(" ")[-1])
        offsets: list[int] = [x for x in range(0, posts, 25)]
        return offsets
    else :
        return []


async def get_image_posts(model: str, offset: int) -> list[str]:
    log.info(f"Getting posts for {model} at offset {offset}")
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as client:
        async with client.get(f"{user_base_url}/{model}?o={offset}") as response:
            await save_cookies(response.cookies, cookie_jar_file)
            soup = BeautifulSoup(await response.text(), "lxml")
        posts = soup.find_all("article", {"class": "post-card"})

    async def get_image(post):
        links: list[str] = []
        if post.find("div", {"class": "post-card__image-container"}):
            link = post.find("h2", {"class": "post-card__heading"}).find("a")["href"]
            links.append(f"{base_coomer}{link}")
        return links

    results = await asyncio.gather(*[get_image(post) for post in posts])
    images = list(chain.from_iterable(results))
    return images


async def get_images_from_post(posts: list[str]) -> list[str]:
    log.info(f"Getting images from posts...")
    client = aiohttp.ClientSession(headers=headers, cookies=cookies)

    async def get_image(url):
        links: list[str] = []
        async with client.get(url) as response:
            await save_cookies(response.cookies, cookie_jar_file)
            soup = BeautifulSoup(await response.text(), "lxml")
        post_files = soup.find_all("div", {"class": "post__files"})
        for file in post_files:
            link = file.find("div", {"class": "post__thumbnail"}).find("a")["href"]
            links.append(f"{base_coomer}{link}")
        return links

    results: list = await asyncio.gather(*[get_image(post) for post in posts])
    await client.close()
    images: list[str] = list(chain.from_iterable(results))
    return images


async def prepare_images(images: list[str]):
    log.info(f"Preparing images for upload...")
    client = aiohttp.ClientSession(headers=headers, cookies=cookies)

    async def process(image):
        async with client.get(image) as response:
            await save_cookies(response.cookies, cookie_jar_file)
            content: io.BytesIO = io.BytesIO(await response.read())
            
        image_size: int = content.getbuffer().nbytes
        if image_size > 1000 and image_size < 25000000:
            file_id = str(uuid.uuid4())
            file = discord.File(content, filename=f'{file_id}.{image.split(".")[-1]}')
            return file
        else:
            log.info(f"Image {image} is too large or too small. Skipping.")
            return None

    image_objects: list = await asyncio.gather(*[process(image) for image in images])
    await client.close()
    images = list(filter(lambda item: item is not None, image_objects))
    return images
