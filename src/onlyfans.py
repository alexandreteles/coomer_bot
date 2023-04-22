import asyncio
import aiohttp
import io
import uuid
from itertools import chain

import discord
import ujson
from bs4 import BeautifulSoup
from loguru import logger as log

from config import *
from src.cookie_utils import *


async def get_models() -> list[dict[str, str]]:
    """Get a list of all creators

    Returns:
        list[dict[str, str]]: JSON with all available models
    """
    cookies: dict[str, str] = await load_cookies(cookie_jar_file)
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as client:
        async with client.get(models_url) as response:
            log.info(f"Getting creators from {models_url}")
            await save_cookies(response.cookies, cookie_jar_file)
            return ujson.loads(await response.text())


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
    cookies: dict[str, str] = await load_cookies(cookie_jar_file)
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as client:
        async with client.get(f"{base_coomer_url}/{model}") as response:
            log.info(f"Getting  data for {model} posts")
            await save_cookies(response.cookies, cookie_jar_file)
            soup = BeautifulSoup(await response.text(), "lxml")
    paginator: str = (
        soup.find("div", class_="paginator", id="paginator-top").findChild("small").text
    )
    posts: int = int(paginator.split(" ")[-1])
    offsets: list[int] = [x for x in range(0, posts, 25)]
    return offsets


async def get_image_posts(model: str, offset: int) -> list[str]:
    log.info(f"Getting posts for {model} at offset {offset}")
    cookies: dict[str, str] = await load_cookies(cookie_jar_file)
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as client:
        async with client.get(f"{base_coomer_url}/{model}?o={offset}") as response:
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
    cookies: dict[str, str] = await load_cookies(cookie_jar_file)
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
    client.close()
    images: list[str] = list(chain.from_iterable(results))
    return images


async def prepare_images(images: list[str]):
    log.info(f"Preparing images for upload...")
    cookies: dict[str, str] = await load_cookies(cookie_jar_file)
    client = aiohttp.ClientSession(headers=headers, cookies=cookies)
    async def process(image):
        async with client.get(image) as response:
            await save_cookies(response.cookies, cookie_jar_file)
            content = io.BytesIO(await response.read())
        file_id = str(uuid.uuid4())
        file = discord.File(content, filename=f'{file_id}.{image.split(".")[-1]}')
        return file

    image_objects: list = await asyncio.gather(*[process(image) for image in images])
    client.close()
    return image_objects
