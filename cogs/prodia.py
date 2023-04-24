import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from loguru import logger as log

from config import *
from src.prodia import generate_image
from views.embeds import generated_image_embed


class ImageGeneration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    prodia: SlashCommandGroup = SlashCommandGroup(
        name="ai",
        description="AI Image Generation"
        )
    
    @prodia.command(
        name="generate",
        description="Generate an image using AI",
    )
    async def generate(
        self,
        ctx: discord.ApplicationContext,
        prompt: discord.Option(str, "Prompt to generate an image from", required=True)
    ):
        await ctx.response.defer(ephemeral=True)
        log.info(f"Generating image...")
        result = await generate_image(prompt)
        if result:
            log.info(f"Generated image successfully.")
            await ctx.followup.send(file=result["file"], ephemeral=True)
            await ctx.followup.send(
                embed=await generated_image_embed(result["metadata"]),
                ephemeral=True
                )
        else:
            await ctx.followup.send(content="Something went wrong.")
