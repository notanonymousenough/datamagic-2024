import aiohttp
import asyncio
import json

class Api:
    url = "https://games.datsteam.dev/play/magcarp/player/move"
    url_test = "https://games-test.datsteam.dev/play/magcarp/player/move"
    url_rounds = "https://games.datsteam.dev/rounds/magcarp"

    def __init__(self, token, debug):
        self.debug = debug
        self.session = aiohttp.ClientSession(headers={"X-Auth-Token": token, "Content-Type": "application/json"})

    async def move(self, req):
        async with self.session.post(url=Api.url_test if self.debug else Api.url) as resp:
            if resp.status != 200:
                print(f"ERR {str(resp.status)}: {await resp.text()}")
                return None
            return json.loads(await resp.text())

    async def close(self):
        await self.session.close()


