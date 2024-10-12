import pygame
import time


# Размеры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = (255, 255, 255)  # Белый фон
PLAYER_COLOR = (0, 0, 255)
PLAYER_WITH_SHIELD_COLOR = (0, 255, 255)
ENEMY_COLOR = (255, 0, 0, 200)  # Красный
ENEMY_WITH_SHIELD_COLOR = (255, 100, 0)  # Красный
BOUNTY_COLOR = (255, 215, 0)  # Золотой цвет
BOUNTY_TARGET_COLOR = (0, 0, 0)  # Золотой цвет
ANOMALY_COLOR_CENTER_POSITIVE = (0, 255, 255, 64)  # Полупрозрачный цвет для аномалий
ANOMALY_COLOR_EFFECTIVITY_POSITIVE = (0, 255, 255, 1)  # Полупрозрачный цвет для аномалий
ANOMALY_COLOR_CENTER_NEGATIVE = (140, 0, 255, 64)  # Полупрозрачный цвет для аномалий
ANOMALY_COLOR_EFFECTIVITY_NEGATIVE = (140, 0, 255, 1)  # Полупрозрачный цвет для аномалий


def map_coordinates(x, y, map_size, screen_size):
    # return int(x * screen_size[0] / map_size['x']), int(y * screen_size[1] / map_size['y'])
    return int(x * screen_size[0] / map_size['x']), int((map_size['y'] - y) * screen_size[1] / map_size['y'])  # инвертировать по вертикали


class GameVisualizer:
    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT, update_interval=0.33):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.fastevent.init()
        self.clock = pygame.time.Clock()
        self.last_update_time = time.time()
        self.update_interval = update_interval
        self.running = True

        # Инициализация шрифта
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)  # Шрифт Arial, размер 24
        self.font_transport = pygame.font.SysFont('Arial', 14)  # Шрифт Arial, размер 24

    def update_screen(self, data, targets):
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
            color = ENEMY_COLOR
            if enemy['shieldLeftMs'] != 0:
                color = ENEMY_WITH_SHIELD_COLOR
            pygame.draw.circle(surface_enemy, color, (enemy_radius, enemy_radius), enemy_radius)
            self.screen.blit(surface_enemy, (enemy_x - enemy_radius, enemy_y - enemy_radius))

        # Рисуем аномалии (полупрозрачные)
        for anomaly in data['anomalies']:
            anomaly_x, anomaly_y = map_coordinates(anomaly['x'], anomaly['y'], data['mapSize'], self.screen.get_size())

            # Первая поверхность для круга с радиусом "radius"
            radius = int(anomaly['radius'])
            if anomaly['strength'] >= 0:
                anomaly_color = ANOMALY_COLOR_CENTER_POSITIVE
            else:
                anomaly_color = ANOMALY_COLOR_CENTER_NEGATIVE
            surface_small = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)  # Диаметр
            pygame.draw.circle(surface_small, anomaly_color, (radius, radius), radius)  # Рисуем круг с радиусом
            self.screen.blit(surface_small, (anomaly_x - radius, anomaly_y - radius))  # Смещаем центр круга

            # Вторая поверхность для большого круга с радиусом "effectiveRadius"
            # effective_radius = int(anomaly['effectiveRadius'])
            # surface_large = pygame.Surface((effective_radius * 2, effective_radius * 2), pygame.SRCALPHA)  # Диаметр
            # pygame.draw.circle(surface_large, ANOMALY_COLOR_EFFECTIVITY, (effective_radius, effective_radius),
            #                    effective_radius)  # Круг с радиусом effectiveRadius
            # self.screen.blit(surface_large,
            #             (anomaly_x - effective_radius, anomaly_y - effective_radius))  # Смещаем центр круга

        for bounty in targets:
            bounty_x, bounty_y = map_coordinates(bounty['x'], bounty['y'], data['mapSize'], self.screen.get_size())
            pygame.draw.circle(self.screen, BOUNTY_TARGET_COLOR, (bounty_x, bounty_y), bounty['radius'])

        # Рисуем игроков
        for i, player in enumerate(data['transports']):
            player_x, player_y = map_coordinates(player['x'], player['y'], data['mapSize'], self.screen.get_size())
            color = PLAYER_COLOR
            if player['shieldLeftMs'] != 0:
                color = PLAYER_WITH_SHIELD_COLOR
            pygame.draw.circle(self.screen, color, (player_x, player_y), data['transportRadius'])

            # Отображаем номер транспорта рядом с кругом
            number_text = self.font.render(str(i + 1), True, (0, 0, 0))  # Черный цвет для номера
            self.screen.blit(number_text, (player_x + data['transportRadius'] + 5, player_y - 10))

        # Отображаем очки
        points_text = f"Points: {data['points']}"
        points_surface = self.font.render(points_text, True, (0, 0, 0))  # Черный цвет текста
        text_width = points_surface.get_width()
        self.screen.blit(points_surface, (self.screen.get_width() - text_width - 10, 10))  # Координаты (10, 10) для отступа от углов

        # transports info
        self.draw_transport_info(data['transports'])

        pygame.display.flip()

    def draw_transport_info(self, data):
        offset_y = 10  # Смещение по Y для каждого нового транспорта
        for i, transport in enumerate(data):
            # Основная информация
            info_lines = [
                f"Transport {i + 1}:",
                f"  position: x={transport['x']}, y={transport['y']}",
                f"  velocity: x={transport['velocity']['x']}, y={transport['velocity']['y']}",
                f"  selfAcceleration: x={transport['selfAcceleration']['x']}, y={transport['selfAcceleration']['y']}",
                f"  anomalyAcceleration: x={transport['anomalyAcceleration']['x']}, y={transport['anomalyAcceleration']['y']}",
                f"  health: {transport['health']}",
                f"  status: {transport['status']}",
                f"  deathCount: {transport['deathCount']}"
            ]

            # Отрисовка каждой строки информации
            for j, line in enumerate(info_lines):
                text_surface = self.font_transport.render(line, True, (0, 0, 0))  # Белый текст
                self.screen.blit(text_surface, (10, offset_y + j * 16))  # Смещение каждой строки на 20 пикселей по Y

            # Обновляем смещение для следующего транспорта
            offset_y += len(info_lines) * 20 + 10  # Добавляем небольшой отступ между транспортами

    def step(self, data_source, targets):
        if not self.running:
            self.close()
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        data = data_source()  # Получаем обновленные данные из внешнего источника
        targets = targets()
        self.update_screen(data, targets)

        self.clock.tick(60)

    def close(self):
        pygame.quit()