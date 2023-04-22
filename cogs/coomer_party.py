from itertools import islice

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from loguru import logger as log

from config import *
from src.onlyfans import *
from views.embeds import model_info_embed


class CoomerParty(commands.Cog):
    def __init__(self, bot, client):
        self.bot = bot
        self.client = client
    
    onlyfans = SlashCommandGroup(name="onlyfans", description="OnlyFans commands")
    
    @onlyfans.command(
        name="info",
        description="Check if a model is available and return relevant information",
    )
    async def info(
        self,
        ctx: discord.ApplicationContext,
        name: discord.Option(str, "Name of the model to search for", required=True),
    ):
        await ctx.response.defer(ephemeral=True)
        log.info(f"Searching for {name}")
        result = await get_model_info(name.lower())
        if result:
            await ctx.followup.send(
                embed=await model_info_embed(result)
            )
        else:
            await ctx.followup.send(
                f"Damn! There is no data available for {name}."
            )

    @onlyfans.command(
        name="photos",
        description="Get the latest photos from a model",
    )
    async def photos(
        self,
        ctx: discord.ApplicationContext,
        name: discord.Option(str, "Name of the model to search for", required=True),
    ):
        await ctx.response.defer(ephemeral=True)
        log.info(f"Searching for {name}")
        image_posts = await get_image_posts(name.lower(), 0, self.client)
        if image_posts:
            images = await get_images_from_post(image_posts, self.client)
            files = await prepare_images(images, self.client)
            log.info(f"Sending {len(files)} images")
            if len(files) > 10:
                splits = [
                    list(islice(files, i, i + 10)) for i in range(0, len(files), 10)
                ]
                for split in splits:
                    await ctx.followup.send(files=split)
            else:
                await ctx.followup.send(files=files)
            log.info(f"Sent {len(files)} images")
        else:
            await ctx.followup.send(
                f"Damn! There is no data available for {name}."
            )
