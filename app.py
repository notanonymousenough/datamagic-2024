import asyncio
import threading

from api import Api
from threading import Thread
from mock import mocked_json, random_modifier
from visualizer import GameVisualizer
from geo_functions import *

MAX_VELOCITY = 50

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
            print(self.last_req)
            res = await self.api.move(self.last_req)
            # print(res)
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
        wanted_list = self.last_data['wantedList']
        bounties = self.last_data['bounties']

        map_size = self.last_data['mapSize']

        max_speed = self.last_data['maxSpeed']
        max_accel = self.last_data['maxAccel']

        attack_range = self.last_data['attackRange']
        attack_cooldown_ms = self.last_data['attackCooldownMs']
        attack_damage = self.last_data['attackDamage']
        attack_explosion_radius = self.last_data['attackExplosionRadius']

        shield_time_ms = self.last_data['shieldTimeMs']
        shield_cooldown_ms = self.last_data['shieldCooldownMs']


        targets = []
        for transport in transports:
            top_target = self.rate_targets(transport, anomalies, enemies, wanted_list, bounties)
            targets.append(top_target)
            acc = self.reach_target_acceleration(transport, top_target, map_size, max_accel)
            attack = self.rate_bandits_and_enemies(transport, wanted_list, enemies)
            shield = self.need_shield(transport, wanted_list)
            req['transports'].append(self.get_transport(transport, acc['x'], acc['y'], shield, attack['x'], attack['y']))
        return req, targets

    def rate_targets(self, transport, anomalies, enemies, wanted_list, bounties):
        return get_nearest_bounty(transport, bounties)

    def rate_bandits_and_enemies(self, transport, wanted_list, enemies):
        n = {'x': None, 'y': None}
        transport_x = transport["x"]
        transport_y = transport["y"]

        max_bounty = 0
        best_bandit = {'x':0, 'y':0}

        # для типов с доски почета
        for bandit in wanted_list:
            bandit_x = bandit["x"]
            bandit_y = bandit["y"]

            # Calculate the distance between the transport and the bandit
            distance = math.sqrt((bandit_x - transport_x) ** 2 + (bandit_y - transport_y) ** 2)

            # Check if the distance is <= 200 and if the bandit's killBounty is the highest
            if distance <= 200 and bandit["killBounty"] > max_bounty and bandit['shieldLeftMs'] == 0:
                max_bounty = bandit["killBounty"]
                best_bandit = bandit
        if best_bandit != {'x':0, 'y':0}:
            return best_bandit

        # для обычных типов
        max_bounty = 0
        best_enemy = {'x':0, 'y':0}
        for enemy in enemies:
            enemy_x = enemy["x"]
            enemy_y = enemy["y"]
            distance = math.sqrt((enemy_x - transport_x) ** 2 + (enemy_y - transport_y) ** 2)
            if distance <= 200 and enemy["killBounty"] > max_bounty and enemy['shieldLeftMs'] == 0:
                max_bounty = enemy["killBounty"]
                best_enemy = enemy
        if best_enemy != {'x': 0, 'y': 0}:
            return best_enemy
        return n

    def reach_target_acceleration(self, transport, target, map_size, max_accel):
        # go to target
        acc = get_max_vector_to_target(transport, target['x'], target['y'])
        distance_to_target = (acc['x']**2 + acc['y']**2)**0.5

        # invert anomaly acceleration
        acc['x'] -= transport['anomalyAcceleration']['x']
        acc['y'] -= transport['anomalyAcceleration']['y']

        # go from walls
        acc = adjust_force_to_stay_within_field(map_size, {'x': transport['x'], 'y': transport['y']}, transport['velocity'], acc)

        # make velocity small
        velocity_k = distance_to_target/200
        if abs(transport['velocity']['x']) > MAX_VELOCITY*velocity_k:
            acc['x'] = -transport['velocity']['x'] * 3
        if abs(transport['velocity']['y']) > MAX_VELOCITY*velocity_k:
            acc['y'] = -transport['velocity']['y'] * 3

        return scale_to_max_available_acceleration(acc['x'], acc['y'], max_accel)

    def need_shield(self, transport, enemies):
        shield_left_ms = transport['shieldLeftMs']
        shield_cooldown_ms = transport['shieldCooldownMs']
        if shield_left_ms != 0 or shield_cooldown_ms != 0:
            return False
        for enemy in enemies:
            d = get_max_vector_to_target(transport, enemy['x'], enemy['y'])
            if d['x'] <= 200 and d['y'] <= 200:
                return True
        return False

    def get_transport(self, transport, acc_x, acc_y, use_shield, attack_x, attack_y):
        req = dict()
        req.update({
            "acceleration": {
                "x": 0,
                "y": 0
            },
            "activateShield": False,
            "attack": {
                "x": 0,
                "y": 0
            },
            "id": "00000000-0000-0000-0000-000000000000"
        })
        req['acceleration']['x'] = acc_x
        req['acceleration']['y'] = acc_y
        req['activateShield'] = use_shield
        req['attack']['x'] = attack_x
        req['attack']['y'] = attack_y
        req['id'] = transport['id']
        return req

    async def close(self):
        await self.api.close()
        self.visualizer.close()
