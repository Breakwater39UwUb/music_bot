import discord
from discord.ext import commands
from discord import app_commands
import db

class SpendShare(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(SpendShare(bot))
