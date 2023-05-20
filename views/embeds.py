import discord

from config import *


async def model_info_embed(service: str, model: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"Model data for {model['id']}",
        description=f"This includes the basic information about the model",
        color=discord.Colour.blurple(),
    )
    embed.set_author(name=bot_name, icon_url=avatar_url)
    embed.set_thumbnail(url=f"{icon_base_url}/{service}/{model['id']}")
    embed.set_image(url=f"{banner_base_url}/{service}/{model['id']}")

    embed.add_field(name="First appeared", value=model["indexed"], inline=True)
    embed.add_field(name="Last update", value=model["updated"], inline=True)

    return embed


async def loading_more_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Loading more pictures...",
        description="Please wait while we load more pictures for you",
        color=discord.Colour.blurple(),
    )
    embed.set_author(name=bot_name, icon_url=avatar_url)

    return embed


async def no_data_available_embed(name: str) -> discord.Embed:
    embed = discord.Embed(
        title="No data available",
        description=f"There is no data available for {name}",
        color=discord.Colour.blurple(),
    )
    embed.set_author(name=bot_name, icon_url=avatar_url)

    return embed


async def unloading_results_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Unloading results",
        description="We are unloading your request to save resources. If you want to continue, please use the command again.",
        color=discord.Colour.blurple(),
    )
    embed.set_author(name=bot_name, icon_url=avatar_url)

    return embed


async def no_more_pictures_embed() -> discord.Embed:
    embed = discord.Embed(
        title="No more pictures",
        description="There are no more pictures available for this model",
        color=discord.Colour.blurple(),
    )
    embed.set_author(name=bot_name, icon_url=avatar_url)

    return embed


async def generated_image_embed(image_data) -> discord.Embed:
    embed = discord.Embed(
        title="AI Image Generation",
        description="Those are the parameters used to generate the image",
        color=discord.Colour.blurple(),
    )
    embed.set_author(name=bot_name, icon_url=avatar_url)
    embed.add_field(name="Prompt", value=image_data["params"]["prompt"])
    embed.add_field(name="Negative Prompt", value=image_data["params"]["prompt"])
    embed.add_field(name="Seed", value=image_data["params"]["seed"], inline=True)
    embed.add_field(
        name="CFG scale", value=image_data["params"]["cfg_scale"], inline=True
    )
    embed.add_field(
        name="Generation steps", value=image_data["params"]["steps"], inline=True
    )
    embed.add_field(
        name="Sampler", value=image_data["params"]["sampler_name"], inline=True
    )
    embed.add_field(
        name="Model",
        value=image_data["params"]["options"]["sd_model_checkpoint"],
        inline=True,
    )

    return embed
