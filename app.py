import asyncio

import pygame

from api import Api
from threading import Thread
from visualizer import GameVisualizer
from mock import mocked_json, random_modifier


class App:
    def __init__(self, token: str, debug: bool):
        self.debug = debug
        self.api = Api(token, debug)
        self.visualizer = GameVisualizer()
        self.last_data = mocked_json

    async def run(self):
        req = None
        while True:
            res = await self.api.move(req)
            if res is None and self.debug:
                random_modifier(self.last_data)
            else:
                self.last_data = res
            self.visualizer.step(lambda: self.last_data)
            await asyncio.sleep(1 / 3)

    async def close(self):
        await self.api.close()
        self.visualizer.close()
