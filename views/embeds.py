import discord
from config import *

async def model_info_embed(model: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"Model data for {model['id']}",
        description=f"This includes the basic information about the model",
        color=discord.Colour.blurple(),
    )
    embed.set_author(name="Coomer", icon_url=avatar_url)
    embed.set_thumbnail(url=f"{icon_base_url}{model['id']}")
    embed.set_image(url=f"{banner_base_url}{model['id']}")

    embed.add_field(name="First appeared", value=model["indexed"], inline=True)
    embed.add_field(name="Last update", value=model["updated"], inline=True)

    return embed
