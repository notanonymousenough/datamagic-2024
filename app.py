import asyncio
import threading

from api import Api
from threading import Thread
from mock import mocked_json, random_modifier
from visualizer import GameVisualizer
from geo_functions import *


class App:
    def __init__(self, token: str, debug: bool):
        self.debug = debug
        self.api = Api(token, debug)
        self.visualizer = GameVisualizer()
        self.last_data = mocked_json

    async def run(self):
        req = {
            "transports": []
        }
        while True:
            res = await self.api.move(req)
            if res is None and self.debug:
                random_modifier(self.last_data)
            else:
                self.last_data = res
            self.visualizer.step(lambda: self.last_data)
            req = await self.update_transports()
            await asyncio.sleep(1 / 3)

    async def update_transports(self):
        req = {
            "transports": []
        }

        transports = self.last_data['transports']
        bounties = self.last_data['bounties']

        for transport in transports:
            target_bounty = get_nearest_bounty(transport, bounties)
            # target_bounty = find_most_profitable_bounty(transport, bounties)
            acc = get_max_vector_to_target(transport, target_bounty['x'], target_bounty['y'], 10)
            tr_req = get_transport(transport, acc['x'], acc['y'], False, 0, 0)
            req['transports'].append(tr_req)
        return req

    async def close(self):
        await self.api.close()
        # self.visualizer.close()
