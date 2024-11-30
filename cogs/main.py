import discord
from discord.ext import commands
from discord import app_commands
import db

# 定義名為 Main 的 Cog
class Main(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command()
    async def Hello(self, ctx: commands.Context):
        await ctx.send("Hello, world!")

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send(f'Ping: {self.bot.latency*1000:.0f}ms')

    @commands.command()
    async def DB(self, ctx: commands.Context, command, arg):
        if command == "show_all":
            result = db.fetch_all(arg)
        await ctx.send(f"{result}")

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(Main(bot))
