import aiohttp
import asyncio
import json
import os
import bpy
import ssl
import certifi


class HeatAPIClient:
    # base_url = "https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/movements"
    base_url = "https://partner-api.heat.tech/prod/v1/movements"
    download_dir = os.getenv('TEMP') or '/tmp'
    sslcontext = ssl.create_default_context(cafile=certifi.where())
    timeout = aiohttp.ClientTimeout(total=90)

    def get_user_api_key_header(self):
        this_plugin_name = __name__.split(".")[0]
        heat_user_api_key = bpy.context.preferences.addons[this_plugin_name].preferences.heat_user_api_key
        return {"X-API-KEY": heat_user_api_key}


    async def get_movements(self):
        header = self.get_user_api_key_header()
        async with aiohttp.ClientSession(headers=header, timeout=self.timeout) as session:
            async with session.get(self.base_url, ssl=self.sslcontext) as resp:
                assert resp.status == 200
                data = await resp.json()
                return data["movements"]

    async def download_file(self, url, file_path, caller=None):
        header = self.get_user_api_key_header()
        async with aiohttp.ClientSession(headers=header, timeout=self.timeout) as session:
            async with session.get(url, ssl=self.sslcontext) as resp:
                if resp.status == 200:
                    total_size = int(resp.headers.get('Content-Length', 0))
                    downloaded_size = 0
                    with open(file_path, 'wb') as fd:
                        while True:
                            chunk = await resp.content.read(1024)
                            downloaded_size += len(chunk)

                            if caller:
                                caller.download_progress = (downloaded_size / total_size)
                            if not chunk:
                                break
                            fd.write(chunk)