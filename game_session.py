import pygame
import random
import time
from config import CELL_SIZE
from player import Player
from enemy import Enemy

# Імпортуємо нові обгортки
from wrapper import MazeWrapper, CoinWrapper


class GameSession:
    def __init__(self, assets):
        self.assets = assets
        self.game_mode = "PvE"

        # Об'єкти C++
        self.maze = None
        self.coins = None

        # Кеш для малювання
        self.map_data = []
        self.texture_data = []

        # Гравці
        self.player1 = None
        self.player2 = None

        self.curr_w = 0
        self.curr_h = 0
        self.seed = 0

    def start_new(self, w, h, mode="PvE"):
        self.game_mode = mode
        self.curr_w = w
        self.curr_h = h
        self.seed = int(time.time())
        self._init_level()

    def load_save(self, save_data):
        self.game_mode = save_data.get('mode', 'PvE')
        self.curr_w = save_data['map']['w']
        self.curr_h = save_data['map']['h']
        self.seed = save_data['map']['seed']
        self._init_level()

        # Відновлення стану гравців
        if 'p1' in save_data and self.player1:
            self.player1.x = save_data['p1']['x']
            self.player1.y = save_data['p1']['y']
            self.player1.score = save_data['p1']['score']

        if 'p2' in save_data and self.player2:
            self.player2.x = save_data['p2']['x']
            self.player2.y = save_data['p2']['y']
            self.player2.score = save_data['p2']['score']

    def _init_level(self):
        # 1. Створення C++ об'єктів
        self.maze = MazeWrapper(self.curr_w, self.curr_h)
        self.map_data = self.maze.generate(self.seed)

        # Генерація текстур
        variants = getattr(self.assets, 'wall_variants_count', 1)
        self.texture_data = self.maze.generate_textures(variants)

        # Монети
        self.coins = CoinWrapper(self.maze)
        self.coins.spawn(int(self.curr_w * self.curr_h * 0.1))

        # 2. СПАВН ГРАВЦІВ (ВИПРАВЛЕНО ЛОГІКУ БОТІВ)

        # --- Player 1 (Лівий) ---
        if self.game_mode == "EvE":
            # Якщо режим Бот проти Бота, то Player 1 теж стає Enemy
            self.player1 = Enemy(1, 1, self.assets, self.maze, self.coins)
        else:
            # Інакше це людина
            self.player1 = Player(1, 1, self.assets, "WASD", self.maze, self.coins)

        # --- Player 2 (Правий) ---
        if self.game_mode == "PvP":
            self.player2 = Player(self.maze.real_w - 2, self.maze.real_h - 2,
                                  self.assets, "ARROWS", self.maze, self.coins)
        else:
            # PvE або EvE -> Другий гравець це бот
            self.player2 = Enemy(self.maze.real_w - 2, self.maze.real_h - 2,
                                 self.assets, self.maze, self.coins)

    def update(self, keys):
        # Оновлення Player 1
        if self.player1.is_bot:
            self.player1.update()  # Бот не потребує клавіш
        else:
            self.player1.update(keys)  # Людина потребує клавіш

        # Оновлення Player 2
        if self.player2:
            if self.player2.is_bot:
                self.player2.update()
            else:
                self.player2.update(keys)

        # Умова перемоги: монети закінчилися
        active_coins = self.coins.get_active_coins_list()
        return len(active_coins) > 0

    def draw(self, surf1, surf2):
        self._draw_view(surf1, self.player1)
        if self.player2:
            self._draw_view(surf2, self.player2)

    def _draw_view(self, surface, focus_target):
        surface.fill((20, 20, 20))

        cam_x = focus_target.x * CELL_SIZE - surface.get_width() // 2
        cam_y = focus_target.y * CELL_SIZE - surface.get_height() // 2

        start_x = max(0, cam_x // CELL_SIZE)
        end_x = min(self.maze.real_w, (cam_x + surface.get_width()) // CELL_SIZE + 1)
        start_y = max(0, cam_y // CELL_SIZE)
        end_y = min(self.maze.real_h, (cam_y + surface.get_height()) // CELL_SIZE + 1)

        # ВИПРАВЛЕННЯ 2: Малюємо підлогу ЗАВЖДИ, а стіни зверху
        floor_img = self.assets.get_image('floor')

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                idx = y * self.maze.real_w + x
                screen_x = x * CELL_SIZE - cam_x
                screen_y = y * CELL_SIZE - cam_y

                # 1. Спочатку завжди малюємо підлогу (щоб під стіною не було дірки)
                surface.blit(floor_img, (screen_x, screen_y))

                # 2. Якщо це стіна - малюємо її зверху
                if self.map_data[idx] == 0:
                    tex_idx = self.texture_data[idx]
                    wall_img = self.assets.get_wall_texture(tex_idx)
                    surface.blit(wall_img, (screen_x, screen_y))

        # Малювання монет
        active_coins = self.coins.get_active_coins_list()
        for c in active_coins:
            cx = c['x'] * CELL_SIZE - cam_x
            cy = c['y'] * CELL_SIZE - cam_y
            if -CELL_SIZE < cx < surface.get_width() and -CELL_SIZE < cy < surface.get_height():
                img = self.assets.get_coin_texture(c['type'])
                surface.blit(img, (cx, cy))

        # Малювання гравців
        self.player1.draw(surface, cam_x, cam_y)
        if self.player2:
            self.player2.draw(surface, cam_x, cam_y)