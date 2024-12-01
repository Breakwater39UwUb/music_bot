import os
import json
import asyncio
from typing import Literal

import aiofiles
import discord
from discord import app_commands
from discord.ext import commands

from dataclass import (
    Features,
    ChannelProfile,
    GuildProfile
)
import utils

bot_log = utils.My_Logger(__file__, 20, filename='bot')
cmd_log = utils.My_Logger(__file__, 20, filename='command history')

class GuildConfigManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.profilePath = './guild_profiles'

    # TODO: Add a function for other commands can see corresponding channels to send.

    @app_commands.command(
        name='gen_guild_profile',
        description='Generates a guild profile for bot to send messages to right channels.'
    )
    async def gen_guild_profile(self, iact: discord.Interaction):
        cmd_log.log(f'{self.gen_guild_profile.callback.__name__} was called by {iact.user.name}')
        await iact.response.defer(ephemeral=True, thinking=True)
        try:
            profile = GuildProfile(name=iact.guild.name,
                                   id=iact.guild.id,
                                   featured_channel={})
            result = await self.write_profile_to_file(profile)
            completion_msg = f'Profile created, full content as follow:\n```json\n{result}```'
            await iact.followup.send(completion_msg, ephemeral=True)
        except Exception as e:
            err_msg = f'Error generating profile: {e}'
            bot_log.log(err_msg, 40)
            await iact.followup.send(err_msg, ephemeral=True)

    async def write_profile_to_file(self, profile: GuildProfile):
        try:
            file_path = f'{self.profilePath}/{profile.id}.json'
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # TODO: Avoid overwriting profile and make sure profile only creates once per guilds.
            async with aiofiles.open(file_path, 'w') as file:
                profile = profile.model_dump(mode='json', exclude='action')
                profile_json = json.dumps(profile, indent=4)
                await file.write(profile_json)
                bot_log.log(f'Profile written to file: {file_path}.')
            return profile_json
        except Exception as e:
            bot_log.log(f'Error writing profile to file: {file_path} - {e}', 40)

    @app_commands.command(
        name='set_channel_for',
        description='Designates a channel for specific features.'
    )
    @app_commands.describe(feature='module to reload')
    async def set_channel_for(self, interaction: discord.Interaction, feature: Features):
        cmd_log.log(f'{self.set_channel_for.callback.__name__} called by {interaction.user.display_name}')
        await interaction.response.defer(ephemeral=True, thinking=True)

        # TODO: Check authorized user access
        try:
            channel = ChannelProfile(name=interaction.channel.name,
                                     id=interaction.channel.id)
            await self.set_channel(interaction.guild.id, feature, channel)
            completion_msg = f'{channel.name} is now set for`{feature.value}`.'
            bot_log.log(completion_msg)
            # TODO: Perform a try catch here, the follup is not sending
            await interaction.followup.send(completion_msg, ephemeral=True)
        except asyncio.TimeoutError:
            err_msg = f'{self.set_channel_for.callback.__name__} `{feature.value}` timed out.'
            bot_log.log(err_msg, 40)
            await interaction.followup.send(err_msg, ephemeral=True)
        except Exception as e:
            err_msg = f'Error setting channel for `{feature.value}:` {e}'
            bot_log.log(err_msg, 40)
        except:
            raise

    async def set_channel(self, guild_id: str, feature: Features, channel: ChannelProfile):
        file_path = f'{self.profilePath}/{guild_id}.json'
        async with aiofiles.open(file_path, 'r') as file:
            data = await file.read()
            data = json.loads(data)
            try:
                data['featured_channel'][feature.value]['name'] = channel.name
                data['featured_channel'][feature.value]['id'] = channel.id
            except KeyError:
                data['featured_channel'][feature.value] = {'name': channel.name, 'id': channel.id}

        async with aiofiles.open(file_path, mode='w') as file:
            await file.write(json.dumps(data, indent=4))
            # TODO: Perform a try catch here, the log is not logging.
            bot_log.log(f"Channel: {data['featured_channel'][feature]['name']} was set.")

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(GuildConfigManager(bot))