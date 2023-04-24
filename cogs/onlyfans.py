import asyncio
from itertools import islice

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.ui import Button, View
from loguru import logger as log

from config import *
from src.onlyfans import *
from views.embeds import *


class OnlyFans(commands.Cog):
    def __init__(self, bot):
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
            await ctx.followup.send(embed = await no_data_available_embed(name))

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
        offsets = await get_model_posts_offsets(name.lower())
        
        if not offsets:
            await ctx.followup.send(embed = await no_data_available_embed(name))
            return
        
        log.info(f"Found {len(offsets)} offsets")
        
        async def send_images(name: str, offset: int):
            image_posts = await get_image_posts(name, offset)
            if image_posts:
                images = await get_images_from_post(image_posts)
                files = await prepare_images(images)
                log.info(f"Sending {len(files)} images")
                if len(files) > 10:
                    splits = [
                        list(islice(files, i, i + 10)) for i in range(0, len(files), 10)
                    ]
                    for split in splits:
                        await ctx.followup.send(
                            files=split,
                            ephemeral=True,
                        )
                else:
                    await ctx.followup.send(
                        files=files,
                        ephemeral=True,
                    )
                log.info(f"Sent {len(files)} images")

        if len(offsets) == 1:
            await send_images(name.lower(), offsets[0])
            await ctx.send_followup(embed = await no_more_pictures_embed(), ephemeral=True) 
        elif len(offsets) > 1:
            for offset in offsets:
                await send_images(name.lower(), offset)
                if offset != offsets[-1]:
                    def check(interaction):
                        return (
                            interaction.channel.id == ctx.channel.id
                            and interaction.user.id == ctx.author.id
                            )
                        
                    cancel_button: Button = Button(style=discord.ButtonStyle.danger, label="Cancel")
                    load_more_button: Button = Button(style=discord.ButtonStyle.primary, label="Load More...")
                    view: View = View()
                    view.add_item(cancel_button)
                    view.add_item(load_more_button)
                    
                    msg = await ctx.send_followup(view=view, ephemeral=True)
                    log.info(f"Awaiting button press...")

                    try:
                        interaction = await self.bot.wait_for(
                            "interaction", check=check, timeout=120
                        )

                        if f"{load_more_button.custom_id}" in str(interaction.data):
                            log.info(f"Load more button pressed, loading...")
                            await msg.delete()
                            await ctx.send_followup(
                                embed=await loading_more_pictures_embed(),
                                ephemeral=True
                                )
                        elif f"{cancel_button.custom_id}" in str(interaction.data):
                            log.info(f"Cancel button pressed, unloading...")
                            await msg.delete()
                            await ctx.send_followup(
                                embed=await unloading_results_embed(),
                                ephemeral=True
                                )
                            break

                    except asyncio.TimeoutError:
                        await msg.delete()
                        await ctx.send_followup(
                            embed=await unloading_results_embed(),
                            ephemeral=True
                            )
                        break
            await ctx.send_followup(embed = await no_more_pictures_embed(), ephemeral=True) 
        else:
            await ctx.followup.send(embed = await no_data_available_embed(name))
