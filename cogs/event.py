import discord
from discord.ext import commands
import json
import time
from cogs.music import Music
import utils

bot_log = utils.My_Logger(__file__, 20, filename='bot')
cmd_log = utils.My_Logger(__file__, 20, filename='command history')

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 當機器人完成啟動時
    @commands.Cog.listener()
    async def on_ready(self):
        slash = await self.bot.tree.sync()
        bot_log.log(f'目前登入身份 --> {self.bot.user}')
        bot_log.log(f'載入 {len(slash)} 個斜線指令')

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.content == 'Hello':
            # await message.channel.send('Hello, world!')
            print('Hello, world!')

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.context, err):
        bot_log.log(f'on_command_error: {err}')
        await ctx.send(err)

    @commands.Cog.listener()
    async def on_error(event, *args, **kwargs):
        bot_log.log(f'onerror: args: {args}, kwargs: {kwargs}')

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.command.name == 'share_song':
            pass
        # if interaction.data['components'][1]['components'][0]['value']:
        #     # reply = View.ModalClass(title='Confirm Artist.')
        #     # await interaction.response.send_modal(reply)
        #     await self.bot.reply('Song title reply')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # TODO: Only send to the channel which was set for this feature
        channel = member.guild.text_channels[0]
        # role = guild.get_role(716186881007812628)
        embed = discord.Embed(title='成員加入', color=0x00fffb)
        embed.set_thumbnail(url=f'{member.avatar}')
        embed.add_field(name='暱稱', value=f'{member}', inline=False)
        embed.add_field(name='加入時間', value=f'{time.ctime(time.time())}', inline=True)
        embed.set_footer(text='歡迎!')
        await channel.send(embed=embed)
        # await member.add_roles(role)

    # @bcommands.Cog.listener()
    # async def on_voice_state_update(self, member,before,after):
    #     channel1 = bot.get_channel(789490220931874817)

    #     if before.channel != after.channel and after.channel != None :
    #             embed=discord.Embed(title=f'{member} 加入了{after.channel}',color=0x2bff00)
    #             embed.add_field(name='時間', value=f'{time.ctime(time.time())}', inline=False)
    #             await channel1.send(embed=embed)
    #     elif after.channel == None :
    #             embed=discord.Embed(title=f'{member} 離開了{before.channel}',color=0xff0000)
    #             embed.add_field(name='時間', value=f'{time.ctime(time.time())}', inline=False)
    #             await channel1.send(embed=embed)
                    
    # @bcommands.Cog.listener()
    # async def on_message_edit(self, before, after):
    #     if before.content != after.content:
    #             channel = bot.get_channel(789490220931874817) #大小事的頻道(ID:789490220931874817)
    #             embed=discord.Embed(title=f'{before.channel}', color=0xfff700)
    #             embed.set_author(name='更改紀錄')
    #             embed.set_thumbnail(url=f'{before.author.avatar_url}')
    #             embed.add_field(name='作者', value=f'{before.author}', inline=False)
    #             embed.add_field(name='before>>>', value=f'{before.content}', inline=True)
    #             embed.add_field(name='after>>>', value=f'{after.content}', inline=False)
    #             embed.set_footer(text=f'{time.ctime(time.time())}')
    #             await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Event(bot))