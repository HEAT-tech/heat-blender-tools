import aiohttp
import asyncio
import json

class HeatAPIClient:
    base_url = "https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/tmp-movements"

    async def get_movements(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url) as resp:
                data = await resp.json()
                for movement in data["movements"]:
                    print(movement["name"])
