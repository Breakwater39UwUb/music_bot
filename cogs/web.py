'''
This COG file uses `aiohttp` to implement http communication.
This web server can not restart along the COG reload method.
'''

import os
import json
import aiohttp
from aiohttp import web
from discord.ext import commands, tasks
import discord
from dataclass import CogRequest

# using fastAPI
from fastapi import FastAPI, Response
app = FastAPI()

class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.web_server.start()
        self.webserver_port = int(os.environ.get('PORT', 5000))

        @app.get('/')
        async def welcome():
            return "Hello, world"

        @app.get('/check_status')
        async def check_status():
            status = self.bot.is_ready()
            return web.Response(text = str(status))

        @app.get('/guilds')
        async def guilds():
            guilds = [guild for guild in self.bot.guilds]
            guildList = [
                {'No.': i + 1, 'name': guild.name, 'id': guild.id}
                for i, guild in enumerate(guilds)
            ]
            guildList = json.dumps(guildList)
            return Response(guildList, 200, media_type='application/json')

        @app.post('/test')
        async def dblwebhook(request):
            # Ignore this, this is a example
            if request.headers.get('authorization') == '3mErTJMYFt':
                data = await request.json()
            return 200

        @app.post('/cog')
        async def cog_interface(request: CogRequest):
            cogManager = self.bot.get_cog('BotManger')

            if request.method == 'load':
                result = await cogManager.load_from_web(module = request.file)
            elif request.method == 'unload':
                result = await cogManager.unload_from_web(module = request.file)
            elif request.method =='reload':
                result = await cogManager.reload_from_web(module = request.file)
            else:
                return Response('Invalid method', 400)

            if result['result'] == 'Fail':
                code = 500
            elif result['result'] == 'Success':
                code = 200

            result = json.dumps(result, indent=4)
            print(result)
            return Response(content = result, status_code = code, media_type='application/json')

    @tasks.loop()
    async def web_server(self):
        import uvicorn  # Import uvicorn here to avoid circular imports
        config = uvicorn.Config(app, host="127.0.0.1", port=self.webserver_port)
        server = uvicorn.Server(config)
        await server.serve()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Webserver(bot))