import re
import json
import asyncio
import datetime
import discord
from discord.ext import commands, tasks
from discord import app_commands
from PIL import Image
import db
import utils

bot_log = utils.My_Logger(__file__, 20, filename='bot')
cmd_log = utils.My_Logger(__file__, 20, filename='command history')

class SpendShare(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open('msg_emoji.json', 'r') as file:
            self.emoji = json.load(file)[0]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        try:
            if '$$' in message.content:
                user = (message.author.id, message.author.name)
                cmd_log.log(f'Spend share was called by {message.author.name}')
                match = re.search(r'\$\$(\d+)', message.content)
                if match:
                    cost = match.group(1)
                    data = (user[1], cost)
                    db.insert_to_table(data=data, table=db.TABLES['spend_share'])
                await message.channel.send(content=cost)

            if message.content == '$show_rank':
                cmd_log.log(f'show_rank was called by {message.author.name}')
                rankings = db.get_spend_ranking('v_currentmonthrank')
                # TODO: Only send to the channel which was set for this feature
                channel_id = message.channel.id
                channel = self.bot.get_channel(channel_id)
                embed=discord.Embed(title='Week Ranking', description='Summary spending ranking of week in this month', color=0x39c5bb)
                # embed.set_thumbnail(url=thumbnail)
                for user in rankings:
                    value = f'{self.emoji["money_with_wings"]} {user[1]} $NTD'
                    embed.add_field(name=user[0], value=value, inline=False)
                await channel.send(embed = embed)
        except Exception as e:
            err_msg = f'Failed to submit spend share.\n```{e}```'
            bot_log.log(err_msg, 40)
            await message.channel.send(err_msg)

class Task(commands.Cog):
    # 臺灣時區 UTC+8
    tz = datetime.timezone(datetime.timedelta(hours = 8))

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.week_ranking.start()

    @tasks.loop(hours=3)
    async def week_ranking(self):
        '''Show week ranking of the month.'''
        # 0 = monday, 1 = tuesday...
        weekday = datetime.datetime.weekday(datetime.datetime.now())
        try:
            if weekday == 6:
                await asyncio.sleep(self.seconds_until(18, 0))
                cmd_log.log('Week ranking was automatically called.')
                rankings = db.get_spend_ranking('v_currentmonthrank')
                channel_id = 1300332787508842599
                channel = self.bot.get_channel(channel_id)
                embed=discord.Embed(title='Week Ranking', description='Summary spending ranking of this month', color=0x39c5bb)
                # embed.set_thumbnail(url=thumbnail)
                for user in rankings:
                    embed.add_field(name=user[2], value=f'{user[0]}: `{int(user[1])}`', inline=False)
                await channel.send(embed = embed)
        except Exception as e:
            err_msg = f'Failed to calculate week ranking.\n{e}'
            bot_log.log(err_msg, 40)
            await channel.send(err_msg)

    def seconds_until(self, hours, minutes):
        '''Calculates the time in seconds until hh:mm is reached'''
        given_time = datetime.time(hours, minutes)
        now = datetime.datetime.now()
        future_exec = datetime.datetime.combine(now, given_time)
        if (future_exec - now).days < 0: # If we are past the execution, it will take place tomorrow
            future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time) # days always >= 0
        return (future_exec - now).total_seconds()

def reduce_image_file_size(fnmIn, fnmOut, factor):
    '''
    Reduce image file size.
    '''
    try:
        img = Image.open(fnmIn)
        img = img.reduce(factor)
        img.save(fnmOut)    
    except Image.DecompressionBombError as ex1:
        print(ex1)
    except Exception as ex2:
        raise ex2

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(SpendShare(bot))
    await bot.add_cog(Task(bot))
