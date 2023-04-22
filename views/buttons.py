import discord

class NextPhotosOffset(discord.ui.View):
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("You clicked the button!")
