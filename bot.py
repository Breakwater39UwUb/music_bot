import os
import asyncio
import discord
from discord.ext import commands, tasks
import dc_config
import utils

bot_log = utils.My_Logger(__file__, 20, filename='bot')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '!', intents = intents)

# 一開始bot開機需載入全部程式檔案
async def load_extensions():
    bot_log.log('Loading cogs...')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
    bot_log.log('Cogs loaded.')

async def main():
    async with bot:
        await load_extensions()
        bot_log.log('Bot starting...')
        await bot.start(dc_config.TOKEN, reconnect=True)
        bot_log.log('Bot started!')

# 確定執行此py檔才會執行
if __name__ == '__main__':
    asyncio.run(main())