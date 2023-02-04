import aiohttp
import asyncio
import json
import os


class HeatAPIClient:
    base_url = "https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/tmp-movements"
    headers = {"X-API-KEY": "HEATDEV"}
    download_dir = os.getenv('TEMP') or '/tmp'

    async def get_movements(self):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.base_url) as resp:
                data = await resp.json()
                return data["movements"]

    async def download_file(self, url, file_path):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(file_path, 'wb') as fd:
                        while True:
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            fd.write(chunk)