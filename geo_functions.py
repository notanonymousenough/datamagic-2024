import math
from datetime import datetime


def get_max_vector_to_target(transport, x2, y2, max_acceleration):
    x1, y1 = transport['x'], transport['y']
    vector_x = x2 - x1
    vector_y = y2 - y1

    # Возвращаем результирующий вектор ускорения
    return {"x": vector_x, "y": vector_y}

def scale_to_max_available_acceleration(x, y, max_acceleration):
    # Длина вектора AB
    vector_length = math.sqrt(x ** 2 + y ** 2)

    # Если длина вектора больше максимального ускорения, масштабируем его
    if vector_length > max_acceleration:
        scaling_factor = max_acceleration / vector_length
        x *= scaling_factor
        y *= scaling_factor
    return {"x": x, "y": y}

def get_nearest_bounty(transport, bounties):
    # Координаты корабля
    transport_x = transport["x"]
    transport_y = transport["y"]

    # Инициализируем минимальное расстояние как бесконечность
    nearest_bounty = None
    max_score = -float('inf')
    # Проходим по списку монеток и находим ближайшую
    for bounty in bounties:
        bounty_x = bounty["x"]
        bounty_y = bounty["y"]
        bounty_points = bounty["points"]

        # Рассчитываем евклидово расстояние
        distance = math.sqrt((bounty_x - transport_x) ** 2 + (bounty_y - transport_y) ** 2)
        if distance == 0:
            continue
        score = bounty_points / distance
        # Обновляем ближайшую монетку, если нашли ближе и дороже
        if score > max_score:
            max_score = score
            nearest_bounty = bounty

    return nearest_bounty


def calculate_cosine_similarity(vx1, vy1, vx2, vy2):
    # Вычисляем косинус угла между двумя векторами
    dot_product = vx1 * vx2 + vy1 * vy2
    magnitude_v1 = math.sqrt(vx1 ** 2 + vy1 ** 2)
    magnitude_v2 = math.sqrt(vx2 ** 2 + vy2 ** 2)

    # Защита от деления на ноль
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0

    return dot_product / (magnitude_v1 * magnitude_v2)


def find_most_profitable_bounty(transport, bounties, max_distance=400):
    # Координаты и скорость корабля
    transport_x = transport["x"]
    transport_y = transport["y"]
    velocity_x = transport["velocity"]['x']
    velocity_y = transport["velocity"]['y']

    # Инициализируем "лучшую" монету как None и минимальный оценочный показатель как бесконечность
    best_bounty = None
    best_score = float('inf')

    for bounty in bounties:
        bounty_x = bounty["x"]
        bounty_y = bounty["y"]

        # Рассчитываем вектор от корабля до монеты
        vector_to_bounty_x = bounty_x - transport_x
        vector_to_bounty_y = bounty_y - transport_y

        # Рассчитываем расстояние до монеты
        distance = math.sqrt(vector_to_bounty_x ** 2 + vector_to_bounty_y ** 2)

        # Пропускаем монету, если расстояние до неё больше 400
        if distance > max_distance:
            continue

        # Рассчитываем "выгодность" по углу между скоростью и вектором до монеты
        cos_similarity = calculate_cosine_similarity(
            velocity_x, velocity_y, vector_to_bounty_x, vector_to_bounty_y
        )

        # Чем больше cos_similarity (ближе к 1) и чем меньше расстояние, тем выгоднее монета
        score = distance / (cos_similarity + 1e-5)  # Добавляем маленькое число, чтобы избежать деления на ноль

        # Обновляем лучшую монету, если она выгоднее
        if score < best_score:
            best_score = score
            best_bounty = bounty

    return best_bounty if best_bounty else None

def adjust_force_to_stay_within_field(field_size, position, speed, force):
    # Вычисляем будущее положение с учётом текущей скорости и силы
    new_speed = {'x': speed['x'] + force['x'], 'y': speed['y'] + force['y']}
    new_position = {'x': position['x'] + new_speed['x'], 'y': position['y'] + new_speed['y']}

    # Корректируем вектор силы, чтобы оставаться в пределах поля
    adjusted_force = {'x': force['x'], 'y': force['y']}

    if new_position['x'] < 0:
        adjusted_force['x'] = -position['x'] - speed['x']
    elif new_position['x'] >= field_size['x']:
        adjusted_force['x'] = field_size['x'] - 1 - position['x'] - speed['x']

    if new_position['y'] < 0:
        adjusted_force['y'] = -position['y'] - speed['y']
    elif new_position['y'] >= field_size['y']:
        adjusted_force['y'] = field_size['y'] - 1 - position['y'] - speed['y']

    return adjusted_force
