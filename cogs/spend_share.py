import re
import datetime
import discord
from discord.ext import commands, tasks
from discord import app_commands
from PIL import Image
import db

class SpendShare(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # @app_commands.command(name = 'share_spend', description = 'Share your spendings!')
    # @app_commands.describe(cost='spending costs', shareMsg='Comment of your spending.',attachment1 = 'Pictures of what you spended for.')
    # async def share_spend(self, interaction: discord.Interaction, cost: str, shareMsg: str,
    #                       attachment1: discord.Attachment = None, attachment2: discord.Attachment = None,
    #                       attachment3: discord.Attachment = None, attachment4: discord.Attachment = None,
    #                       attachment5: discord.Attachment = None, attachment6: discord.Attachment = None):
    #     user = (interaction.user.id, interaction.user.name)
    #     try:
    #         await interaction.response.defer()

    #         attachmentUrls = ''
    #         for attachment in (attachment1, attachment2, attachment3, attachment4, attachment5, attachment6):
    #             if attachment is not None:
    #                 # attachments += f'[ ]({attachment.url})\n'
    #                 attachmentUrls += f'{attachment.url}\n'

    #         await interaction.followup.send(f'{cost}\n{attachmentUrls}')
    #     except Exception as e:
    #         err_msg = f'Failed to submit song.\n```{e}```'
    #         await interaction.followup.send(err_msg, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        try:
            if '$$' in message.content:
                user = (message.author.id, message.author.name)
                match = re.search(r'\$\$(\d+)', message.content)
                if match:
                    cost = match.group(1)
                    data = (user[1], cost)
                    db.insert_to_table(data=data, table=db.TABLES['spend_share'])
                await message.channel.send(content=cost)
                # print('Hello, world!')
        except Exception as e:
            err_msg = f'Failed to submit spend share.\n```{e}```'
            await message.channel.send(err_msg, ephemeral=True)

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
