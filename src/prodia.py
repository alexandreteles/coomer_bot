import asyncio
import io
import os
import uuid

import aiohttp
import discord
import ujson
from loguru import logger as log

from config import *


async def generate_image(prompt: str, seed: int = -1) -> dict[str, str | dict]:
    """
    Generates an image given a prompt and seed value.

    Args:
        prompt (str): The text prompt to generate the image from.
        seed (int, optional): The seed value to use. Defaults to -1.

    Returns:
        dict[str, str | dict]: A dictionary containing information about the generated image.
    """

    log.info(f"Generating image...")
    prodia_headers: dict[str, str] = {
        "X-Prodia-Key": os.environ.get("PRODIA_TOKEN"),
        "accept": "application/json",
        "content-type": "application/json",
    }
    payload: dict[str, str | int | bool] = {
        "model": model,
        "prompt": f"{prompt_prefix}{prompt}",
        "negative_prompt": negative_prompt,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "seed": seed,
        "upscale": upscale,
        "sampler": sampler,
        "aspect_ratio": aspect_ratio,
    }

    async with aiohttp.ClientSession(
        headers=prodia_headers, json_serialize=ujson.dumps
    ) as client:
        async with client.post(prodia_url, json=payload) as response:
            log.debug(f"Got response from Prodia.")
            generated_image_data: dict = {}
            if response.status != 200:
                return {}

            job: dict = await response.json(loads=ujson.loads)
            if not job["job"]:
                return {}

            log.debug(f"Got job ID {job['job']}.")
            status: str = ""
            counter: int = 0

            async def check_job_status():
                nonlocal status, counter, generated_image_data
                while status != "succeeded":
                    if counter > 12:
                        log.error(f"Job timed out.")
                        break

                    async with client.get(f"{prodia_url}/{job['job']}") as job_response:
                        log.debug(f"Got status {status}.")
                        status = (await job_response.json(loads=ujson.loads))["status"]

                        if status == "failed":
                            log.error(f"Job failed.")
                            break

                        elif status == "succeeded":
                            log.debug(f"Job succeeded.")
                            generated_image_data["metadata"] = await job_response.json(
                                loads=ujson.loads
                            )
                            log.debug(f"Got generated image.")
                            break

                        counter += 1
                        await asyncio.sleep(5)

            # Run the job status check concurrently with a timeout
            try:
                await asyncio.wait_for(
                    asyncio.ensure_future(check_job_status()), timeout=60
                )
            except asyncio.TimeoutError:
                log.error(f"Job timed out.")

        if not generated_image_data.get("metadata"):
            return {}

        async with client.get(generated_image_data["metadata"]["imageUrl"]) as response:
            if response.status != 200:
                return {}

            log.debug(f"Got image.")
            image = io.BytesIO(await response.read())
            file_id = str(uuid.uuid4())
            generated_image_data["file"] = discord.File(
                image, filename=f"{file_id}.png"
            )

            return generated_image_data
