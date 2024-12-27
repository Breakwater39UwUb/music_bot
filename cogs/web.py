import os
import json
import asyncio
from flask import Flask, jsonify, request, Response
from discord.ext import commands, tasks
import utils
from dataclass import (
    CogRequest,
    actionRequest,
    GuildProfile
)

# 初始化日誌記錄器
bot_log = utils.My_Logger(__file__, 20, filename='bot')
cmd_log = utils.My_Logger(__file__, 20, filename='command history')

# 初始化 Flask
flask_app = Flask(__name__)

class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flask_port = int(os.environ.get('FLASK_PORT', 5887))
        self.web_server.start()

        # Flask 路由設定
        @flask_app.route('/')
        def welcome():
            return jsonify({"message": "Hello, world"}), 200

        @flask_app.route('/check_status', methods=['GET'])
        def check_status():
            '''檢查機器人是否在線。'''
            user = 'Unknown'
            cmd_log.log(f'{check_status.__name__} called by {user}')
            try:
                status = self.bot.is_ready()
                return jsonify({"status": status}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @flask_app.route('/get_guilds', methods=['GET'])
        def get_guilds():
            '''取得機器人加入的伺服器列表。'''
            user = 'Unknown'
            cmd_log.log(f'{get_guilds.__name__} called by {user}')
            guilds = [guild for guild in self.bot.guilds]
            guild_list = [
                {'No.': i + 1, 'name': guild.name, 'id': guild.id}
                for i, guild in enumerate(guilds)
            ]
            return jsonify(guild_list), 200

        @flask_app.route('/cog', methods=['POST'])
        def cog():
            '''管理 COG 的載入、卸載與重新載入。'''
            user = 'Unknown'
            cmd_log.log(f'{cog.__name__} called by {user}')
            cog_manager = self.bot.get_cog('BotManger')
            data = request.get_json()

            if data['method'] == 'load':
                result = asyncio.run(cog_manager.load_from_web(module=data['file']))
            elif data['method'] == 'unload':
                result = asyncio.run(cog_manager.unload_from_web(module=data['file']))
            elif data['method'] == 'reload':
                result = asyncio.run(cog_manager.reload_from_web(module=data['file']))
            else:
                return jsonify({"error": "Invalid method"}), 400

            code = 200 if result['result'] == 'Success' else 500
            return jsonify(result), code

        @flask_app.route('/bot_action', methods=['POST'])
        def bot_action():
            '''執行機器人相關操作，例如重啟或登出。'''
            user = 'Unknown'
            data = request.get_json()

            if data['action'] == 'restart':
                cog = self.bot.get_cog('Main')
                cmd_log.log(f'restart called by {user}')
                cog.restart_bot()

            return Response(status=200)

        @flask_app.route('/gen_guild_profile', methods=['POST'])
        def gen_guild_profile():
            '''創建伺服器設定檔。'''
            user = 'Unknown'
            cmd_log.log(f'gen_guild_profile called by {user}')
            conf_manager = self.bot.get_cog('GuildConfigManager')
            data = request.get_json()

            try:
                result = conf_manager.save_guild_profile(data)
                return jsonify(result), 200
            except Exception as e:
                bot_log.log(f'Error generating profile: {e}', 40)
                return jsonify({"error": str(e)}), 500

        @flask_app.route('/load_guild_profile', methods=['POST'])
        def load_guild_profile():
            '''從 JSON 文件加載伺服器設定檔。'''
            user = 'Unknown'
            cmd_log.log(f'load_guild_profile called by {user}')
            conf_manager = self.bot.get_cog('GuildConfigManager')
            data = request.get_json()

            try:
                guild_id = data.get('guild_id')
                result = conf_manager.load_guild_profile(guild_id) if guild_id else conf_manager.load_guild_profile()
                result_json = Webserver.dataclass_to_json(result)
                return jsonify(result_json), 200
            except Exception as e:
                bot_log.log(f'Error loading profile: {e}', 40)
                return jsonify({"error": str(e)}), 500

    @staticmethod
    def dataclass_to_json(obj):
        '''將 dataclass 轉換為 JSON 字串。'''
        if isinstance(obj, dict):
            converted_dict = [prof.model_dump(mode='python', exclude='action') for prof in obj.values()]
            return converted_dict
        elif isinstance(obj, GuildProfile):
            return obj.model_dump(mode='python', exclude='action')
        return {}

            # TODO: Fix error occur after restart: OSError: [Errno 48] Address already in use
    @tasks.loop()
    async def web_server(self):
        from threading import Thread

        def start_flask():
            flask_app.run(host="0.0.0.0", port=self.flask_port)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, start_flask)

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Webserver(bot))