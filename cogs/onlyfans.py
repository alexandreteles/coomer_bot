import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.ui import Button, View
from loguru import logger as log
import asyncio
from typing import Final

from config import *
from src.onlyfans import *
from views.embeds import *


class OnlyFans(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

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
            await ctx.followup.send(embed=await model_info_embed(result))
        else:
            await ctx.followup.send(embed=await no_data_available_embed(name))

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

        async def send_images(images: list[str]):
            # images = await get_image_posts(name, offset)
            # if not images:
            #     return
            files = await prepare_images(images)
            log.debug(f"Sending {len(files)} images")
            await ctx.followup.send(
                files=files,
                ephemeral=True,
            )
            log.debug(f"{len(files)} images sent")

        limit: Final[int] = 10  # max allowed attachments per message
        offset = 0
        images = await get_image_posts(name, offset, limit)
        offset += len(images)
        if not images:
            await ctx.send_followup(embed=no_data_available_embed(name), ephemeral=True)
            return

        await send_images(images)
        if len(images) < limit:
            log.debug(f"Only {len(images)}/{limit} images found, not loading more")
            await ctx.send_followup(embed=no_more_pictures_embed(), ephemeral=True)
            return

        def check(interaction):
            return (
                interaction.channel.id == ctx.channel.id
                and interaction.user.id == ctx.author.id
            )

        while True:
            cancel_button: Button = Button(
                style=discord.ButtonStyle.danger, label="Cancel"
            )
            load_more_button: Button = Button(
                style=discord.ButtonStyle.primary, label="Load more"
            )
            view = View()
            view.add_item(cancel_button)
            view.add_item(load_more_button)
            msg = await ctx.send_followup(view=view, ephemeral=True)
            log.debug(f"Awaiting button press...")

            try:
                interaction = await self.bot.wait_for(
                    "interaction", check=check, timeout=120
                )
                if f"{load_more_button.custom_id}" in str(interaction.data):
                    await msg.delete()
                    loading_msg = await ctx.send_followup(
                        embed=loading_more_embed(), ephemeral=True
                    )
                    images = await get_image_posts(name, offset, limit)
                    if not images:
                        await msg.delete()
                        await ctx.send_followup(
                            embed=no_more_pictures_embed(), ephemeral=True
                        )
                        await loading_msg.delete()
                        break
                    offset += len(images)
                    await send_images(images)
                    await loading_msg.delete()
                elif f"{cancel_button.custom_id}" in str(interaction.data):
                    raise asyncio.TimeoutError  # cheesy, but it works
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.send_followup(embed=unloading_results_embed(), ephemeral=True)
                log.debug(f"Unloading results...")
                break
