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
        self.last_req = {
            "transports": []
        }

    async def run(self):
        while True:
            res = await self.api.move(self.last_req)
            print(res)
            if res is None and self.debug:
                random_modifier(self.last_data)
            else:
                self.last_data = res
            self.last_req, targets = await self.update_transports()
            self.visualizer.step(lambda: self.last_data, lambda: targets)
            await asyncio.sleep(1 / 3)

    async def update_transports(self):
        req = {
            "transports": []
        }

        transports = self.last_data['transports']
        anomalies = self.last_data['anomalies']
        enemies = self.last_data['enemies']
        wantedList = self.last_data['wantedList']
        bounties = self.last_data['bounties']

        mapSize = self.last_data['mapSize']

        maxSpeed = self.last_data['maxSpeed']
        maxAccel = self.last_data['maxAccel']

        attackRange = self.last_data['attackRange']
        attackCooldownMs = self.last_data['attackCooldownMs']
        attackDamage = self.last_data['attackDamage']
        attackExplosionRadius = self.last_data['attackExplosionRadius']

        shieldTimeMs = self.last_data['shieldTimeMs']
        shieldCooldownMs = self.last_data['shieldCooldownMs']


        targets = []
        for transport in transports:
            top_target = self.rate_targets(transport, anomalies, enemies, wantedList, bounties)
            targets.append(top_target)
            tr_req = self.reach_target(transport, top_target)
            req['transports'].append(tr_req)
        return req, targets

    def rate_targets(self, transport, anomalies, enemies, wantedList, bounties):
        return get_nearest_bounty(transport, bounties)

    def reach_target(self, transport, target):
        acc = get_max_vector_to_target(transport, target['x'], target['y'], 10)
        tr_req = get_transport(transport, acc['x'], acc['y'], False, 0, 0)
        return tr_req

    async def close(self):
        await self.api.close()
        self.visualizer.close()
