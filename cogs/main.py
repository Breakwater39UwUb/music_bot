import os
import sys
import discord
from discord.ext import commands
from discord import app_commands
import db
import utils

bot_log = utils.My_Logger(__file__, 20, filename='bot')
cmd_log = utils.My_Logger(__file__, 20, filename='command history')

# 定義名為 Main 的 Cog
class Main(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command()
    async def Hello(self, ctx: commands.Context):
        cmd_log.log(f'{self.Hello.callback.__name__} called by {ctx.author}')
        await ctx.send("Hello, world!")

    @commands.command()
    async def ping(self, ctx: commands.Context):
        cmd_log.log(f'{self.ping.callback.__name__} called by {ctx.author}')
        await ctx.send(f'Ping: {self.bot.latency*1000:.0f}ms')

    def restart_bot(self): 
        bot_log.log('Restarting bot.')
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command()
    async def restart(self, ctx: commands.Context):
        cmd_log.log(f'{self.restart.callback.__name__} called by {ctx.author}')

        # TODO: Add if statement to verify that the command was authorized by guild profiles
        await ctx.send("Restarting bot...")
        self.restart_bot()

    @commands.command()
    async def DB(self, ctx: commands.Context, command, arg):
        if command == "show_all":
            result = db.fetch_all(arg)
        await ctx.send(f"{result}")

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(Main(bot))
