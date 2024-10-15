import os
import enum
import discord
from discord.app_commands.translator import locale_str
from db import fetch_tags

class SongTags(discord.ui.Select):
    def __init__(self, type: str):
        tags = fetch_tags(type=type)
        placeholder = f'Select a song {type}.'
        options = [discord.SelectOption(label=tag) for tag in tags]
        super().__init__(placeholder=placeholder, min_values=0, options=options)
    async def callback(self, interaction: discord.Interaction):

        await interaction.response.send_message(self.values[0],ephemeral=True)
