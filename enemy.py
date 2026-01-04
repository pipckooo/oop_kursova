# enemy.py
import pygame
from config import CELL_SIZE


class EnemyRenderer:
    """Цей клас тепер відповідає ТІЛЬКИ за малювання. Логіки тут немає."""

    def __init__(self, assets):
        self.assets = assets
        self.img_idle = assets.get_image('p2_idle')
        # Анімацію поки спростимо, або можна передавати isMoving з C++ пізніше
        self.img = self.img_idle

    def draw(self, surface, x, y, cam_x, cam_y):
        screen_x = x * CELL_SIZE - cam_x
        screen_y = y * CELL_SIZE - cam_y

        # Малюємо тільки якщо ворог в межах екрану
        if -CELL_SIZE < screen_x < surface.get_width() and -CELL_SIZE < screen_y < surface.get_height():
            surface.blit(self.img, (screen_x, screen_y))