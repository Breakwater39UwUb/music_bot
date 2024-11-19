import os
import asyncio
import discord
from discord.ext import commands, tasks
import dc_config

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "!", intents = intents)

# 一開始bot開機需載入全部程式檔案
async def load_extensions():
    print("Loading cogs.")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
    print("Cogs loaded.")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(dc_config.TOKEN, reconnect=True)

# 確定執行此py檔才會執行
if __name__ == "__main__":
    asyncio.run(main())