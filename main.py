import os

import discord
from loguru import logger as log

from cogs.onlyfans import OnlyFans
from cogs.prodia import ImageGeneration
from config import *
from src.cookie_utils import load_cookies

bot = discord.Bot(debug_guilds=[guild_id])

try:
    log.info("Loading OnlyFans cog...")
    bot.add_cog(OnlyFans(bot))
    log.info(f"Loaded OnlyFans cog.")
except Exception as e:
    log.error(f"Could not load coomer.party cog: {e}")

try:
    log.info("Loading Prodia cog...")
    bot.add_cog(ImageGeneration(bot))
    log.info(f"Loaded Prodia cog.")
except Exception as e:
    log.error(f"Could not load Prodia cog: {e}")

@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}. Getting some lotion and tissues...")
    log.info("Ready to coom.")


bot.run(os.environ.get("DISCORD_TOKEN"))
