import os
import discord
import aiohttp
import ujson
from loguru import logger as log

from config import *
from src.cookie_utils import load_cookies
from cogs.onlyfans import OnlyFans

bot = discord.Bot(debug_guilds=[guild_id])

try:
    log.info("Loading OnlyFans cog...")
    bot.add_cog(OnlyFans(bot))
    log.info(f"Loaded OnlyFans cog.")
except Exception as e:
    log.error(f"Could not load coomer.party cog: {e}")


@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}. Getting some lotion and tissues...")
    log.info("Ready to coom.")


bot.run(os.environ.get("DISCORD_TOKEN"))
