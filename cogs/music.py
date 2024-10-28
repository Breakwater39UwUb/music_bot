from typing import List
import asyncio
import re
import json
import discord
from discord.ext import commands
from discord.app_commands import Choice
from discord import app_commands
import pymysql.err as sql_err
from PIL import Image
from urllib import request
from urllib.parse import parse_qs, urlparse, urlencode
from ytmusicapi import YTMusic
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

        def __init__(self, timeout: float | None = 180):
        # def __init__(self, songData, timeout: float | None = 180):
            super().__init__(timeout = timeout)
            # self.songData = songData
            '''[0]: song id, [1]: song title, [2]: artist,
            [3]:user id, [4]: url, [5]: thumbnail url'''
            # self.songData.append('') # songData[5], comment by url sharing
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
            await interaction.response.defer(ephemeral=True)

        async def btn_callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.ans = self.children[0].values + self.children[1].values
            try:
                embed=discord.Embed(title='Song submitted', description='The song you want to share has been submitted.', color=0x39c5bb)
                # (ID, title, artist name, user ID)
                # self.songData[4], self.songData[5] = Music.get_thumbnail(self.songData[4]) # comment by url sharing
                artistURL = Music.format_url(self.songData[2])
                embed.set_image(url=self.songData[5])
                embed.add_field(name='Song ID', value=f'```{self.songData[0]}```', inline=False)
                embed.add_field(name='Song title', value=self.songData[1])
                embed.add_field(name='Song artist', value=f'[{self.songData[2]}]({artistURL})')
                embed.add_field(name='Song tags', value=self.ans, inline=False)
                embed.add_field(name='Recommender', value=f'{interaction.user.mention}', inline=False)
                embed.add_field(name='URL', value=f'[Listen]({self.songData[4]})', inline=False) if self.songData[4] != '' else None
                await interaction.followup.send(embed = embed)
            except Exception as e:
                err_msg = f'Failed to submit song.\n{e}'
                await interaction.followup.send(err_msg, ephemeral=True)

    class CompanySelMenu(discord.ui.View):
        def __init__(self, companies, timeout: float | None = 180):
            super().__init__(timeout = timeout)
            options = [discord.SelectOption(label=name, value=id) for id, name in companies]
            companyList = discord.ui.Select(placeholder='Choose a company.',
                                            options=options)
            companyList.callback = self.menu_callback
            self.add_item(companyList)
        async def menu_callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.selectedCompany = interaction.values[0]

    class ModalClass(discord.ui.Modal, title = 'Share your recommendation.'):
        '''
        繼承 discord.ui.Modal 類別，並傳入 title 參數
        '''
        artistNameBox = discord.ui.TextInput(label = 'Artist Name')
        artistAltNameBox = discord.ui.TextInput(label = 'Artist Altnate Name', required=False)

        # Modal 提交後接著要執行的程式碼
        async def on_submit(self, interaction: discord.Interaction):
            # if self.songArtist.value != '':
            #     dynamicModal = View.ModalClass(title='Specify artist.')
            self.artistName = self.artistNameBox.value
            self.artistAltName = self.artistAltNameBox.value
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
                return [
                    Choice(name=artist[1], value=str(artist[0]))
                    for artist in auto_artists
                ]
            else:
                return []
        except sql_err.OperationalError as e:
            print(e)
            await ctx.followup.send(str(e))

    async def song_arg_autocomplete(
        self,
        ctx: discord.Interaction,
        current: str
    ) -> List[Choice[str]]:
        user_option_input = ctx.data.get("options", [{}])[0].get("value")
        artist_name = user_option_input if user_option_input else None
        try:
            if artist_name is not None:
                auto_artists = db.find_artists(artist_name)
                return [
                    Choice(name=artist[1], value=str(artist[0]))
                    for artist in auto_artists
                ]
            else:
                return []
        except sql_err.OperationalError as e:
            print(e)
            await ctx.followup.send(str(e))

    @app_commands.command(name = 'share_song_manual', description = 'Share a song! (Manual input)')
    @app_commands.autocomplete(artist=artist_autocomplete)
    @app_commands.describe(song_title='song title', artist='artist name, if you don\'t know the name, skip it or type "UNKNOWN"', url='song url')
    async def share_song_manual(self, interaction: discord.Interaction,
                         song_title: str, artist: str = '5529', url: str = ''):
        # TODO: Optimize manual input experience
        user = (interaction.user.id, interaction.user.name)
        try:
            await interaction.response.defer(ephemeral=True, thinking = True)
            submitResults = db.submit_song(song_title, artist, user)
            submitResults.append(url)
            view = self.TagSelMenu(submitResults)
            await interaction.followup.send(view = view)
            # tags = await self.bot.wait_for('button_click', check=view.btn_callback)
        except Exception as e:
            err_msg = f'Failed to submit song.\n{e}'
            # await interaction.response.send_message(err_msg, ephemeral=True)
            await interaction.followup.send(err_msg, ephemeral=True)

    @app_commands.command(name = 'share_song', description = 'Share a song by sending a link!')
    # @app_commands.autocomplete(link=song_arg_autocomplete)
    @app_commands.describe(link='song url')
    async def share_song(self, interaction: discord.Interaction, link: str):
        user = (interaction.user.id, interaction.user.name)
        try:
            await interaction.response.defer(ephemeral=True, thinking = True)
            song_args = self.parse_song(link)
            artistResult = db.find_artists(song_args[1])
            if artistResult == []:
                await self.add_artist(interaction, song_args[1])
            song_attr = tuple(db.submit_song(song_args[0], song_args[1], user))
            song_attr += (link, song_args[2])
            view = self.TagSelMenu()
            view.songData = song_attr
            await interaction.followup.send(view = view)
        except Exception as e:
            err_msg = f'Failed to submit song.\n```{e}```'
            await interaction.followup.send(err_msg, ephemeral=True)

    async def add_artist(self, iact: discord.Interaction, artistName):
        await iact.followup.send(f'It looks that the artist, `{artistName}` is not in our database.\nWe are adding this one.')
        await iact.followup.send('Type the Artist Altnate Name, like his name in other languages.(type `-none` to skip)')
        message = await self.bot.wait_for("message", timeout=60.0)
        artistAltName = message.content if message.content != '-none' else None

        await iact.followup.send('Which record company this artist signed to?(type `-none` to skip)')
        message = await self.bot.wait_for("message", timeout=60.0)
        artistCompany = message.content if message.content != '-none' else None
        companyResults = db.find_company(artistCompany) if artistCompany is not None else []
        if companyResults == []:
            await self.add_company(iact, artistCompany)
        else:
            view = self.CompanySelMenu(companyResults)
            await iact.followup.send(view=view)
            wait = await self.bot.wait_for('interaction', timeout=60)
            artistCompany = wait

        db.insert_to_table((artistName, artistAltName, artistCompany), db.TABLES['artists'])

    async def add_company(self, iact:discord.Interaction, companyName: str):
        await iact.followup.send('It looks that the company is not in our database.\nWe are adding this company, give the company alternate name or type `-none` to skip this.')
        message = await self.bot.wait_for("message", timeout=60.0)
        companyAltName = message.content if message.content != '-none' else None
        db.insert_to_table((companyName, companyAltName), db.TABLES['company'])

    def parse_song(self, songLink):
        '''Get song attributes from given song link.
        
        :param songLink: URL of song, valid platforms are
        YouTube, Spotify, Tidal.

        :return songAttr: (Title, Artist, Thumbnails)
        '''
        title = ''
        artist = ''
        thumbnail = ''

        # TODO Implement YouTubeMusic
        if 'youtube' in songLink or 'youtu.be' in songLink:
            yt = YTMusic('oauth.json')
            # TODO check return value from YouTubeMusic
            # TODO implement albums detection (playlist)
            # Consider move url parsing to this function
            linkArgs = self.parse_link(songLink)
            search_results = yt.search(query=linkArgs, limit=2)
            title = search_results[0]['title']
            artist = search_results[0]['artists'][0]['name']
            thumbnail = search_results[0]['thumbnails'][-1]['url']
        return title, artist, thumbnail

        # TODO Implement Spotify

        # TODO Implement Tidal
        # Tidal API requires account login to use, but it is not available in Taiwan
        # https://developer.tidal.com/documentation/api-sdk/api-sdk-quick-start
        # https://developer.tidal.com/apiref

        # TODO Implement Apple Music

    def parse_link(self, url):
        '''Parse the URL to get the query parameters'''
        # TODO: Add Apple Music and Tidal support, this function may merge to parse_song() in the future
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Case 1: Standard YouTube URL (e.g., https://www.youtube.com/watch?v=SdDdyMb0p2U)
        if "v" in query_params:
            return query_params["v"][0]

        # Case 2: Google redirect URL (e.g., https://www.google.com/url?...&url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DSdDdyMb0p2U&...)
        if "url" in query_params:
            youtube_url = query_params["url"][0]
            youtube_parsed = urlparse(youtube_url)
            youtube_query_params = parse_qs(youtube_parsed.query)
            if "v" in youtube_query_params:
                return youtube_query_params["v"][0]

        # Case 3: YouTube short URL (e.g., https://youtu.be/SdDdyMb0p2U)
        short_id_match = re.search(r"youtu\.be/([^?&]+)", url)
        if short_id_match:
            return short_id_match.group(1)

        if parsed_url.path == '/playlist':
            return query_params['list']

        if parsed_url.hostname == 'music.youtube.com':
            return url

        if 'spotify' in url:
            prefix = "https://open.spotify.com/oembed?url="
            thumbnail_url = f"{prefix}{url}"

            x = request.urlopen(thumbnail_url)
            raw_data = x.read()
            encoding = x.info().get_content_charset('utf8')  # JSON default
            data = json.loads(raw_data.decode(encoding))
            return url, data['thumbnail_url']
        return None

    def get_thumbnail(self, url):
            '''Parse the URL to get the query parameters'''
            # TODO: Add Apple Music and Tidal support, this function may merge to parse_song() in the future
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)

            # Case 1: Standard YouTube URL (e.g., https://www.youtube.com/watch?v=SdDdyMb0p2U)
            if "v" in query_params:
                return url, f'https://img.youtube.com/vi/{query_params["v"][0]}/maxresdefault.jpg', query_params["v"][0]

            # Case 2: Google redirect URL (e.g., https://www.google.com/url?...&url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DSdDdyMb0p2U&...)
            if "url" in query_params:
                youtube_url = query_params["url"][0]
                youtube_parsed = urlparse(youtube_url)
                youtube_query_params = parse_qs(youtube_parsed.query)
                if "v" in youtube_query_params:
                    return youtube_url, f'https://img.youtube.com/vi/{youtube_query_params["v"][0]}/maxresdefault.jpg', youtube_query_params["v"][0]

            # Case 3: YouTube short URL (e.g., https://youtu.be/SdDdyMb0p2U)
            short_id_match = re.search(r"youtu\.be/([^?&]+)", url)
            if short_id_match:
                return url, f'https://img.youtube.com/vi/{short_id_match.group(1)}/maxresdefault.jpg', short_id_match.group(1)

            if parsed_url.hostname == 'music.youtube.com':
                return 
            if 'spotify' in url:
                prefix = "https://open.spotify.com/oembed?url="
                thumbnail_url = f"{prefix}{url}"

                x = request.urlopen(thumbnail_url)
                raw_data = x.read()
                encoding = x.info().get_content_charset('utf8')  # JSON default
                data = json.loads(raw_data.decode(encoding))
                return url, data['thumbnail_url']
            return None

    def format_url(data):
        base_url = "https://www.google.com/search?"
        params = {"q": data}

        # Encode the parameters and construct the URL
        corrected_url = base_url + urlencode(params)
        return corrected_url

async def setup(bot: commands.Bot):
    '''Cog 載入 Bot'''
    await bot.add_cog(Music(bot))
