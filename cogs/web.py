'''
This COG file uses `aiohttp` to implement http communication.
This web server can not restart along the COG reload method.
'''

import os
import aiohttp
from aiohttp import web
from discord.ext import commands, tasks
import discord

app = web.Application()
routes = web.RouteTableDef()

class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.web_server.start()

        @routes.get('/')
        async def welcome(request):
            return web.Response(text="Hello, world")
        
        @routes.get('/check_status')
        async def check_status(request):
            status = self.bot.is_ready()
            return web.Response(text = str(status))
        
        @routes.get('/test')
        async def test(request):
            print(type(bot.guilds))
            print(bot.guilds)
            return web.Response(text = str(bot.guilds))
        
        @routes.get('/guilds')
        async def guilds(request):
            guilds = [guild for guild in self.bot.guilds]
            guildProf = [guild.name for guild in guilds]
            return web.Response(text = '\n'.join(guildProf))

        @routes.post('/dbl')
        async def dblwebhook(request):
            # Ignore this, this is a example
            if request.headers.get('authorization') == '3mErTJMYFt':
                data = await request.json()
            return 200

        self.webserver_port = os.environ.get('PORT', 5000)
        app.add_routes(routes)

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='127.0.0.1', port=self.webserver_port)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Webserver(bot))