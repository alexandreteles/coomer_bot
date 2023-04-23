import asyncio
from itertools import islice

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.ui import Button, View
from loguru import logger as log

from config import *
from src.onlyfans import *
from views.embeds import model_info_embed


class NextPhotosOffset(discord.ui.View):
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("You clicked the button!")


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
            await ctx.followup.send(f"Damn! There is no data available for {name}.")

    @onlyfans.command(
        name="photos",
        description="Get the latest photos from a model",
    )
    async def photos(
        self,
        ctx: discord.ApplicationContext,
        name: discord.Option(str, "Name of the model to search for", required=True),
    ):
        def check(interaction):
            return (
                interaction.channel.id == ctx.channel.id
                and interaction.user.id == ctx.author.id
            )

        button: Button = Button(style=discord.ButtonStyle.primary, label="Load More")
        view: View = View()
        view.add_item(button)

        await ctx.response.defer(ephemeral=True)

        log.info(f"Searching for {name}")
        offsets = await get_model_posts_offsets(name.lower())

        if len(offsets) == 1:
            image_posts = await get_image_posts(name.lower(), 0)
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
                            content=f"Latest photos from {name}:",
                            view=NextPhotosOffset(),
                            ephemeral=True,
                        )
                else:
                    await ctx.followup.send(
                        files=files,
                        content=f"Latest photos from {name}:",
                        ephemeral=True,
                    )
                log.info(f"Sent {len(files)} images")
        elif len(offsets) > 1:
            for offset in offsets:
                image_posts = await get_image_posts(name.lower(), offset)
                if image_posts:
                    images = await get_images_from_post(image_posts)
                    files = await prepare_images(images)
                    log.info(f"Sending {len(files)} images")
                    if len(files) > 10:
                        splits = [
                            list(islice(files, i, i + 10))
                            for i in range(0, len(files), 10)
                        ]
                        for split in splits:
                            await ctx.followup.send(
                                files=split,
                                content=f"Latest photos from {name}:",
                                ephemeral=True,
                            )
                    else:
                        await ctx.followup.send(
                            files=files,
                            content=f"Latest photos from {name}:",
                            ephemeral=True,
                        )
                    log.info(f"Sent {len(files)} images")

                    msg = await ctx.send_followup(view=view, ephemeral=True)
                    log.info(f"Awaiting button press...")

                    try:
                        interaction = await self.bot.wait_for(
                            "interaction", check=check, timeout=120
                        )

                        if f"{button.custom_id}" in str(interaction.data):
                            embed = discord.Embed(description=f"Loading more photos...")
                            await msg.delete()
                            await ctx.send_followup(embed=embed, ephemeral=True)

                    except asyncio.TimeoutError:
                        embed = discord.Embed(
                            description=f"We are unloading your request to save resources. If you want to continue, please use the command again."
                        )
                        await msg.delete()
                        await ctx.send_followup(embed=embed, ephemeral=True)
                        break
        else:
            await ctx.followup.send(f"Damn! There is no data available for {name}.")
