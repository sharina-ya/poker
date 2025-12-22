import pygame

# Размеры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750

# Центр стола
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

# Цвета
BACKGROUND = (34, 139, 34)  # Зеленый стол
TABLE_COLOR = (0, 100, 0)
TABLE_BORDER = (139, 69, 19)  # Коричневый
PLAYER_ACTIVE = (255, 215, 0)  # Золотой
PLAYER_INACTIVE = (100, 100, 100)  # Серый
PLAYER_TURN = (255, 255, 150)  # Светло-желтый
CARD_BACK = (25, 25, 112)  # Темно-синий
CARD_FRONT = (255, 255, 255)  # Белый
TEXT_COLOR = (255, 255, 255)
TEXT_DARK = (30, 30, 30)  # Темный текст
BUTTON_COLOR = (220, 20, 60)  # Красный
BUTTON_HOVER = (255, 69, 0)  # Оранжевый
CHIPS_COLOR = (255, 215, 0)  # Золотой для фишек
CHIPS_TEXT_COLOR = (0, 0, 0)  # Черный текст
POT_COLOR = (255, 140, 0)  # Оранжевый для банка
INFO_BG_COLOR = (0, 0, 0, 180)  # Полупрозрачный черный

# Размеры элементов
TABLE_RADIUS = 180  # Радиус игрового стола
PLAYER_RADIUS = 30  # Радиус кружка игрока
CARD_WIDTH = 45
CARD_HEIGHT = 70
CARD_RADIUS = 6
CARD_SPACING = 12

# Позиции игроков для каждого количества (x, y)
# Фиксированные позиции для идеального отображения
PLAYER_POSITIONS = {
    2: [  # 2 игрока: сверху и снизу
        (CENTER_X, 120),  # Верхний
        (CENTER_X, SCREEN_HEIGHT - 120)  # Нижний
    ],
    3: [  # 3 игрока: треугольник
        (CENTER_X, 160),  # Верхний
        (CENTER_X + 100, SCREEN_HEIGHT - 180),  # Правый нижний
        (CENTER_X - 100, SCREEN_HEIGHT - 180)  # Левый нижний
    ],
    4: [  # 4 игрока: квадрат
        (CENTER_X, 120),  # Верхний
        (CENTER_X + 200, CENTER_Y-100),  # Правый
        (CENTER_X, SCREEN_HEIGHT - 120),  # Нижний
        (CENTER_X - 200, CENTER_Y-100)  # Левый
    ]
    ,
    5: [  # 5 игроков: пентагон
        (CENTER_X, 120),  # Верхний
        (CENTER_X + 180, 180),  # Правый верхний
        (CENTER_X + 180, CENTER_Y + 160),  # Правый нижний

        (CENTER_X, SCREEN_HEIGHT - 120),  # Нижний
        (CENTER_X - 200, CENTER_Y + 100)  # Левый нижний
    ],
    6: [  # 6 игроков: шестиугольник
        (CENTER_X, 120),  # Верхний
        (CENTER_X + 180, 160),  # Правый верхний
        (CENTER_X + 180, CENTER_Y + 80),  # Правый нижний
        (CENTER_X, SCREEN_HEIGHT - 120),  # Нижний
        (CENTER_X - 180, CENTER_Y + 80),  # Левый нижний
        (CENTER_X - 180, 160)  # Левый верхний
    ]
}

# Область информации (правая часть)
INFO_AREA_X = SCREEN_WIDTH - 180  # Начинается слева от этой координаты
INFO_AREA_WIDTH = 0

# Позиции кнопок (центрированы внизу)
BUTTONS = {
    "fold": (CENTER_X - 185, SCREEN_HEIGHT - 40),
    "check": (CENTER_X - 105, SCREEN_HEIGHT - 40),
    "call": (CENTER_X - 25, SCREEN_HEIGHT - 40),
    "raise": (CENTER_X + 55, SCREEN_HEIGHT - 40),
    "all_in": (CENTER_X + 135, SCREEN_HEIGHT - 40)
    #"next_player": (CENTER_X + 250, SCREEN_HEIGHT - 40)
}


# Шрифты
def init_fonts():
    pygame.font.init()
    return {
        "title": pygame.font.SysFont("arial", 28, bold=True),
        "player": pygame.font.SysFont("arial", 18, bold=True),
        "card": pygame.font.SysFont("arial", 22, bold=True),
        "button": pygame.font.SysFont("arial", 16, bold=True),
        "info": pygame.font.SysFont("arial", 16),
        "chips": pygame.font.SysFont("arial", 16, bold=True),
        "phase": pygame.font.SysFont("arial", 24, bold=True)
    }


def get_player_positions(num_players):
    """Получить фиксированные позиции для заданного количества игроков"""
    return PLAYER_POSITIONS.get(num_players, PLAYER_POSITIONS[6])[:num_players]


def get_card_positions(player_x, player_y):
    """Получить позиции для двух карт игрока"""
    total_width = 2 * CARD_WIDTH + CARD_SPACING
    start_x = player_x - total_width // 2
    card_y = player_y + PLAYER_RADIUS + 20

    # Проверяем, не выходит ли за границы экрана
    #if card_y + CARD_HEIGHT > SCREEN_HEIGHT - 150:  # Оставляем место для кнопок
        #card_y = player_y - PLAYER_RADIUS - CARD_HEIGHT - 20

    return [
        (start_x, card_y),
        (start_x + CARD_WIDTH + CARD_SPACING, card_y)
    ]


def get_community_card_positions(num_cards):
    """Получить позиции для общих карт"""
    positions = []
    total_width = num_cards * CARD_WIDTH + (num_cards - 1) * CARD_SPACING
    start_x = CENTER_X - total_width // 2
    y = CENTER_Y - 10

    for i in range(num_cards):
        x = start_x + i * (CARD_WIDTH + CARD_SPACING)
        positions.append((x, y))

    return positions
