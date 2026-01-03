# config.py

CELL_SIZE = 40

# Пресети розмірів (Логічна ширина/висота)
# Small: швидка гра
# Medium: стандарт
# Large: довга гра
MAP_SIZES = {
    'SMALL':  (15, 11),
    'MEDIUM': (21, 15),
    'LARGE':  (31, 21)
}

# Розміри вікна (Split-Screen)
VIEW_W = 600
VIEW_H = 600
SCREEN_W = VIEW_W * 2
SCREEN_H = VIEW_H

# Кольори
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
UI_BG = (20, 20, 40)
BTN_COLOR = (50, 50, 150)
BTN_HOVER = (80, 80, 200)
TEXT_GOLD = (255, 215, 0)