import pygame
import time


# Размеры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = (255, 255, 255)  # Белый фон
PLAYER_COLOR = (0, 0, 255)
ENEMY_COLOR = (255, 0, 0, 200)  # Красный
BOUNTY_COLOR = (255, 215, 0)  # Золотой цвет
ANOMALY_COLOR_CENTER = (0, 255, 255, 128)  # Полупрозрачный цвет для аномалий
ANOMALY_COLOR_EFFECTIVITY = (128, 255, 0, 1)  # Полупрозрачный цвет для аномалий


def map_coordinates(x, y, map_size, screen_size):
    return int(x * screen_size[0] / map_size['x']), int(y * screen_size[1] / map_size['y'])


class GameVisualizer:
    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT, update_interval=0.33):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.fastevent.init()
        self.clock = pygame.time.Clock()
        self.last_update_time = time.time()
        self.update_interval = update_interval
        self.running = True

    def update_screen(self, data):
        self.screen.fill(BACKGROUND_COLOR)


        # Рисуем "награды" (bounties)
        for bounty in data['bounties']:
            bounty_x, bounty_y = map_coordinates(bounty['x'], bounty['y'], data['mapSize'], self.screen.get_size())
            pygame.draw.circle(self.screen, BOUNTY_COLOR, (bounty_x, bounty_y), bounty['radius'])

        # Рисуем врагов
        for enemy in data['enemies']:
            enemy_x, enemy_y = map_coordinates(enemy['x'], enemy['y'], data['mapSize'], self.screen.get_size())
            enemy_radius = 5  # Радиус для отображения врагов
            surface_enemy = pygame.Surface((enemy_radius * 2, enemy_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface_enemy, ENEMY_COLOR, (enemy_radius, enemy_radius), enemy_radius)
            self.screen.blit(surface_enemy, (enemy_x - enemy_radius, enemy_y - enemy_radius))

        # Рисуем аномалии (полупрозрачные)
        for anomaly in data['anomalies']:
            anomaly_x, anomaly_y = map_coordinates(anomaly['x'], anomaly['y'], data['mapSize'], self.screen.get_size())

            # Первая поверхность для круга с радиусом "radius"
            radius = int(anomaly['radius'])
            surface_small = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)  # Диаметр
            pygame.draw.circle(surface_small, ANOMALY_COLOR_CENTER, (radius, radius), radius)  # Рисуем круг с радиусом
            self.screen.blit(surface_small, (anomaly_x - radius, anomaly_y - radius))  # Смещаем центр круга

            # Вторая поверхность для большого круга с радиусом "effectiveRadius"
            # effective_radius = int(anomaly['effectiveRadius'])
            # surface_large = pygame.Surface((effective_radius * 2, effective_radius * 2), pygame.SRCALPHA)  # Диаметр
            # pygame.draw.circle(surface_large, ANOMALY_COLOR_EFFECTIVITY, (effective_radius, effective_radius),
            #                    effective_radius)  # Круг с радиусом effectiveRadius
            # self.screen.blit(surface_large,
            #             (anomaly_x - effective_radius, anomaly_y - effective_radius))  # Смещаем центр круга

        # Рисуем игроков
        for player in data['transports']:
            player_x, player_y = map_coordinates(player['x'], player['y'], data['mapSize'], self.screen.get_size())
            pygame.draw.circle(self.screen, PLAYER_COLOR, (player_x, player_y), data['transportRadius'])

        pygame.display.flip()

    def step(self, data_source):
        if not self.running:
            self.close()
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        data = data_source()  # Получаем обновленные данные из внешнего источника
        self.update_screen(data)

        self.clock.tick(60)

    def close(self):
        pygame.quit()