import os
import enum
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

class BotManger(commands.Cog):
    class CogModules(enum.Enum):
        """
        Enumerate for different Cog modules.
        If new module is added, need to add new attribute manually.
        """
        __cogDir__ = 'cogs.'
        all = __cogDir__ + '*'
        main = __cogDir__ + 'main'
        event = __cogDir__ + 'event'
        bot_manager = __cogDir__ + 'bot_manager'
        music = __cogDir__ + 'music'

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name='load_module',
        description='Load Cogs modules'
    )
    @app_commands.describe(module='module to load')
    async def load(self, interaction: discord.Interaction,
                   module: CogModules):
        '''載入指令程式檔案'''
        await self.bot.load_extension(f'{module.value}')
        await interaction.response.send_message(
            f'{module.value} loaded.', ephemeral = True
        )

    @app_commands.command(
        name='unload_module',
        description='Unload Cogs modules'
    )
    @app_commands.describe(module='module to unload')
    async def unload(self, interaction: discord.Interaction,
                     module: CogModules):
        '''卸載指令檔案'''
        await self.bot.unload_extension(f'{module.value}')
        await interaction.response.send_message(
            f'{module.value} unloaded.', ephemeral = True
        )

    @app_commands.command(
        name='reload_module',
        description='Reload Cogs modules'
    )
    @app_commands.describe(module='module to reload')
    async def reload(self, interaction: discord.Interaction,
                     module: CogModules):
        '''
        重新載入程式檔案
        '''
        if module == self.CogModules.all:
            for item in self.CogModules:
                if item == self.CogModules.all:
                    continue
                await self.bot.reload_extension(item.value)
        else:
            await self.bot.reload_extension(f'{module.value}')
        slash = await self.bot.tree.sync()
        print(f"載入 {len(slash)} 個斜線指令")
        await interaction.response.send_message(
            f'`{module.value}` reloaded.', ephemeral=True
        )

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(BotManger(bot))