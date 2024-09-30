import discord
from discord.ext import commands
from discord import app_commands
import db

class View(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.modal1 = self.ModalClass()

    class ViewClass(discord.ui.View):
        '''宣告一個 ViewClass 類別，繼承 discord.ui.View'''
        def __init__(self, timeout: float | None = 180):
            super().__init__(timeout = timeout)
            # 添加一個 Button 到 ViewClass 中
            self.add_item(discord.ui.Button(label = 'Button'))

    # 繼承 discord.ui.Modal 類別，並傳入 title 參數
    class ModalClass(discord.ui.Modal, title = 'Share your recommendation.'):
        # 宣告一個 TextInput Item 元素
        songTitle = discord.ui.TextInput(label = 'Song Title')
        songArtist = discord.ui.TextInput(label = 'Artist Name', required=False)
        # songArtist.value = None
        selector = None

        # Modal 提交後接著要執行的程式碼
        async def on_submit(self, interaction: discord.Interaction):
            if self.songArtist.value != '':
                dynamicModal = View.ModalClass(title='Specify artist.')
                dynamicModal.songTitle = self.songTitle
                await interaction.response.send_modal(dynamicModal)

            await interaction.response.send_message(
                f'Song title: {self.songTitle.value}, Artist: {self.songArtist}')

    @app_commands.command(name = 'share_song', description = 'Share a song!')
    async def share_song(self, interaction: discord.Interaction):
        # 回覆 Modal 給使用者
        await interaction.response.send_modal(self.modal1)

    @app_commands.command(name = 'view_class', description = 'Class 版本 View 範例')
    async def view_class(self, interaction: discord.Interaction):
        # 創建一個 ViewClass 類別，並設置 30 秒超時
        view = self.ViewClass(timeout = 30)
        await interaction.response.send_message(view = view)

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(View(bot))
