from typing import List
import discord
from discord.ext import commands
from discord.app_commands import Choice
from discord import app_commands
from selections import SuggestArtists
import db

class View(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.modal1 = self.ModalClass()

    class ViewClass(discord.ui.View):
        '''宣告一個 ViewClass 類別，繼承 discord.ui.View'''
        def __init__(self, timeout: float | None = 180):
            super().__init__(timeout = timeout)
            self.add_item(SuggestArtists())

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

            view = View.ViewClass(timeout = 30)
            print(view)
            await interaction.response.send_message(view = view)
            # await interaction.response.send_message(
            #     f'Song title: {self.songTitle.value}, Artist: {self.songArtist}')
            # await interaction.response.autocomplete(SuggestArtists)
        async def on_timeout(self):
            print('Timeout on submission.')

    async def artist_autocomplete(
        self,
        ctx: discord.Interaction,
        current: str
    ) -> List[Choice[str]]:
        user_option_input = ctx.data.get("options", [{}])[1].get("value")
        artist_name = user_option_input if user_option_input else None
        if artist_name is not None:
            auto_artists = db.find_artists(artist_name)
            print(auto_artists)
            return [
                Choice(name=artist, value=artist)
                for artist in auto_artists
            ]
        else:
            return []
    @app_commands.command(name = 'share_song', description = 'Share a song!')
    @app_commands.autocomplete(artist=artist_autocomplete)
    async def share_song(self, interaction: discord.Interaction,
                         song_title: str, artist: str):
        # 回覆 Modal 給使用者
        # await interaction.response.send_modal(self.ModalClass())
        interaction.response.send_message(song_title+'\n'+artist)

    @app_commands.command(name = 'view_class', description = 'Class 版本 View 範例')
    async def view_class(self, interaction: discord.Interaction):
        # 創建一個 ViewClass 類別，並設置 30 秒超時
        view = self.ViewClass(timeout = 30)
        await interaction.response.send_message(view = view)

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(View(bot))
