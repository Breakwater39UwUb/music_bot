from typing import List
import asyncio
import discord
from discord.ext import commands
from discord.app_commands import Choice
from discord import app_commands
import pymysql.err as sql_err
import db

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.modal1 = self.ModalClass()

    class TagSelMenu(discord.ui.View):
        class SongTags(discord.ui.Select):
            def __init__(self, type: str):
                tags = db.fetch_tags(type=type)
                placeholder = f'Select a song {type}.'
                options = [discord.SelectOption(label=tag) for tag in tags]
                super().__init__(placeholder=placeholder, min_values=0, max_values=len(options), options=options)

        '''宣告一個 ViewClass 類別，繼承 discord.ui.View'''
        def __init__(self, songData, timeout: float | None = 180):
            super().__init__(timeout = timeout)
            self.songData = songData
            moodMenu = Music.TagSelMenu.SongTags('Mood')
            typeMenu = Music.TagSelMenu.SongTags('Type')
            subBtn = discord.ui.Button(label='Submit')
            moodMenu.callback = self.menu_callback
            typeMenu.callback = self.menu_callback
            subBtn.callback = self.btn_callback
            self.add_item(moodMenu)
            self.add_item(typeMenu)
            self.add_item(subBtn)

        async def menu_callback(self, interaction: discord.Interaction):
            # await interaction.followup.fetch()
            # await interaction.response.send_message(self.values[0])
            await interaction.response.defer(ephemeral=True)
            # self.ans.append(interaction.data['values'])
            # if self.values[0] == "Option 3":
            # await interaction.response.defer(ephemeral=True, thinking=True)
            # await interaction.followup.send(interaction.data['values'], ephemeral=True)

        async def btn_callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.ans = self.children[0].values + self.children[1].values
            try:
                embed=discord.Embed(title='Song submitted', description='The song you want to share has been submitted.', color=0x39c5bb)
                # (ID, title, artist name, user ID)
                embed.add_field(name='Song ID', value=f'```{self.songData[0]}```', inline=False)
                embed.add_field(name='Song title', value=self.songData[1])
                embed.add_field(name='Song artist', value=self.songData[2])
                embed.add_field(name='Song tags', value=self.ans, inline=False)
                embed.add_field(name='Recommender', value=f'{interaction.user.mention}', inline=False)
                embed.add_field(name='URL', value=self.songData[4], inline=False) if self.songData[4] != '' else None
                await interaction.followup.send(embed = embed)
            except Exception as e:
                err_msg = f'Failed to submit song.\n{e}'
                # await interaction.response.send_message(err_msg, ephemeral=True)
                await interaction.followup.send(err_msg, ephemeral=True)

    class ModalClass(discord.ui.Modal, title = 'Share your recommendation.'):
        '''
        繼承 discord.ui.Modal 類別，並傳入 title 參數
        '''
        # 宣告一個 TextInput Item 元素
        songTitle = discord.ui.TextInput(label = 'Song Title')
        songArtist = discord.ui.TextInput(label = 'Artist Name', required=False)
        # songArtist.value = None
        selector = None

        # Modal 提交後接著要執行的程式碼
        async def on_submit(self, interaction: discord.Interaction):
            # if self.songArtist.value != '':
            #     dynamicModal = View.ModalClass(title='Specify artist.')
            #     dynamicModal.songTitle = self.songTitle
            #     await interaction.response.send_modal(dynamicModal)

            view = Music.TagSelMenu(timeout = 30)
            print(view)
            await interaction.response.send_message(view = view)
            # await interaction.response.send_message(
            #     f'Song title: {self.songTitle.value}, Artist: {self.songArtist}')
            # await interaction.response.autocomplete(SongTags)
        async def on_timeout(self):
            print('Timeout on submission.')

    async def artist_autocomplete(
        self,
        ctx: discord.Interaction,
        current: str
    ) -> List[Choice[str]]:
        user_option_input = ctx.data.get("options", [{}])[1].get("value")
        artist_name = user_option_input if user_option_input else None
        try:
            if artist_name is not None:
                auto_artists = db.find_artists(artist_name)
                # print(auto_artists)
                return [
                    Choice(name=artist[1], value=str(artist[0]))
                    for artist in auto_artists
                ]
            else:
                return []
        except sql_err.OperationalError as e:
            # (2003, "Can't connect to MySQL server on '1.170.130.56' (timed out)")
            print(e)
            await ctx.response.send_message(str(e))
    @app_commands.command(name = 'share_song', description = 'Share a song!')
    @app_commands.autocomplete(artist=artist_autocomplete)
    @app_commands.describe(song_title='song title', artist='artist name, if you don\'t know the name, skip it or type "UNKNOWN"', url='song url')
    async def share_song(self, interaction: discord.Interaction,
                         song_title: str, artist: str = '5529', url: str = ''):
        user = (interaction.user.id, interaction.user.name)
        try:
            await interaction.response.defer(ephemeral = True, thinking = True)
            submitResults = db.submit_song(song_title, artist, user)
            submitResults.append(url)
            view = self.TagSelMenu(songData=submitResults)
            await interaction.followup.send(view = view)
            # tags = await self.bot.wait_for('button_click', check=view.btn_callback)
        except Exception as e:
            err_msg = f'Failed to submit song.\n{e}'
            # await interaction.response.send_message(err_msg, ephemeral=True)
            await interaction.followup.send(err_msg, ephemeral=True)

    @app_commands.command(name = 'view_class', description = 'Class 版本 View 範例')
    async def view_class(self, interaction: discord.Interaction):
        # 創建一個 ViewClass 類別，並設置 30 秒超時
        view = self.TagSelMenu(timeout = 30)
        await interaction.response.send_message(view = view)

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(Music(bot))
