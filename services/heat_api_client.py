import aiohttp
import asyncio
import json
import os
import bpy


class HeatAPIClient:
    base_url = "https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/movements"
    headers = {"X-API-KEY": "HEATDEV"}
    download_dir = os.getenv('TEMP') or '/tmp'

    def get_user_api_key_header(self):
        this_plugin_name = __name__.split(".")[0]
        heat_user_api_key = bpy.context.preferences.addons[this_plugin_name].preferences.heat_user_api_key
        return {"X-API-KEY": heat_user_api_key}


    async def get_movements(self):
        header = self.get_user_api_key_header()
        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(self.base_url) as resp:
                data = await resp.json()
                return data["movements"]

    async def download_file(self, url, file_path):
        header = self.get_user_api_key_header()
        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(file_path, 'wb') as fd:
                        while True:
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            fd.write(chunk)