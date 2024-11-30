'''
This COG file uses `aiohttp` to implement http communication.
This web server can not restart along the COG reload method.
'''

import os
import sys
import json
import aiohttp
from aiohttp import web
from discord.ext import commands, tasks
import discord
from dataclass import CogRequest, actionRequest
import utils

# TODO: log should record authorized users, now are "Unknown".
bot_log = utils.My_Logger(__file__, 20, filename='bot')
cmd_log = utils.My_Logger(__file__, 20, filename='command history')

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
            '''A get method to check whether the bot is dead or not.'''
            user = 'Unknown'
            cmd_log.log(f'{check_status.__name__} called by {user}')
            try:
                status = self.bot.is_ready()
                return Response(str(status))
            except Exception as e:
                return web.Response(text=f'Error: {e}', status=500)

        @app.get('/guilds')
        async def guilds():
            '''A get method for guilds that bot are invited in.'''
            user = 'Unknown'
            cmd_log.log(f'{guilds.__name__} called by {user}')
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
        async def cog(request: CogRequest):
            '''A post method for cog management'''
            user = 'Unknown'
            cmd_log.log(f'{cog.__name__} called by {user}')
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
            return Response(content = result, status_code = code, media_type='application/json')

        @app.post('/bot_action')
        async def bot_action(request: actionRequest):
            '''A post action for bot action, ex: restart, logout'''
            user = 'Unknown'
            if request.action == 'restart':
                cog = self.bot.get_cog('Main')
                # TODO: Handle no http response due to process restart.
                cmd_log.log(f'restart called by {user}')
                cog.restart_bot()

        # TODO: implement guild profile creation
        @app.post('/gen_guild_profile')
        async def gen_guild_profile(request):
            pass

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