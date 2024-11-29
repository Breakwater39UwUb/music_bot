import os
import asyncio
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
        spend_share = __cogDir__ + 'spend_share'

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
        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            if module == self.CogModules.all:
                for item in self.CogModules:
                    if item == self.CogModules.all:
                        continue
                    # Reload each module with a 20-second timeout
                    await asyncio.wait_for(self.bot.load_extension(item.value), timeout=20)
            else:
                # Reload the specified module with a 20-second timeout
                await asyncio.wait_for(self.bot.load_extension(f'{module.value}'), timeout=20)

            slash = await self.bot.tree.sync()
            print(f"載入 {len(slash)} 個斜線指令")

            await interaction.followup.send(
                f'`{module.value}` loaded.', ephemeral=True
            )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                f'Error: Loading `{module.value}` timed out after 20 seconds.',
                ephemeral=True
            )

    @app_commands.command(
        name='unload_module',
        description='Unload Cogs modules'
    )
    @app_commands.describe(module='module to unload')
    async def unload(self, interaction: discord.Interaction,
                     module: CogModules):
        '''卸載指令檔案'''
        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            if module == self.CogModules.all:
                for item in self.CogModules:
                    if item == self.CogModules.all:
                        continue
                    # Reload each module with a 20-second timeout
                    await asyncio.wait_for(self.bot.unload_extension(item.value), timeout=20)
            else:
                # Reload the specified module with a 20-second timeout
                await asyncio.wait_for(self.bot.unload_extension(f'{module.value}'), timeout=20)

            slash = await self.bot.tree.sync()
            print(f"載入 {len(slash)} 個斜線指令")

            await interaction.followup.send(
                f'`{module.value}` unloaded.', ephemeral=True
            )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                f'Error: Unloading `{module.value}` timed out after 20 seconds.',
                ephemeral=True
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
        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            if module == self.CogModules.all:
                for item in self.CogModules:
                    if item == self.CogModules.all:
                        continue
                    # Reload each module with a 20-second timeout
                    await asyncio.wait_for(self.bot.reload_extension(item.value), timeout=20)
            else:
                # Reload the specified module with a 20-second timeout
                await asyncio.wait_for(self.bot.reload_extension(f'{module.value}'), timeout=20)

            slash = await self.bot.tree.sync()
            print(f"載入 {len(slash)} 個斜線指令")

            await interaction.followup.send(
                f'`{module.value}` reloaded.', ephemeral=True
            )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                f'Error: Reloading `{module.value}` timed out after 20 seconds.',
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(BotManger(bot))