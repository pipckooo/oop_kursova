#game_session.py
import pygame
import random
from config import *
from wrappers.maze_wrapper import MazeWrapper
from wrappers.coin_wrapper import CoinWrapper
from player import Player
from enemy import Enemy


class GameSession:
    def __init__(self, game_mode, difficulty, assets):
        self.game_mode = game_mode
        self.difficulty = difficulty
        self.assets = assets

        # Розміри (логічні)
        if difficulty == "Easy":
            self.curr_w, self.curr_h = 15, 11
        elif difficulty == "Medium":
            self.curr_w, self.curr_h = 25, 19
        else:
            self.curr_w, self.curr_h = 35, 25

        self.seed = random.randint(0, 999999)
        self._init_level()

        # --- ДОДАЙ ЦЕЙ МЕТОД ТУТ ---
    def start_new(self, w, h, mode):
        self.curr_w = w
        self.curr_h = h
        self.game_mode = mode
        self.seed = random.randint(0, 999999)
        self._init_level()
        #



    def _init_level(self):
        # 1. ГЕНЕРАЦІЯ
        self.maze = MazeWrapper(self.curr_w, self.curr_h)
        self.map_data = self.maze.generate(self.seed)

        variants = getattr(self.assets, 'wall_variants_count', 1)
        self.texture_data = self.maze.generate_textures(variants)

        rw = self.maze.real_w
        rh = self.maze.real_h


        p1_x, p1_y = 1, 1
        found = False

        for y in range(1, rh - 1):
            for x in range(1, rw - 1):
                if self.maze.is_walkable(x, y):
                    p1_x, p1_y = x, y
                    found = True
                    break
            if found: break  # <--- Зупиняємо зовнішній цикл!

        print(f"[Spawn] Player 1 at: {p1_x}, {p1_y}")


        p2_x, p2_y = self.maze.real_w - 2, self.maze.real_h - 2
        attempts = 0
        while attempts < 100:
            rx = random.randint(self.maze.real_w // 2, self.maze.real_w - 2)
            ry = random.randint(self.maze.real_h // 2, self.maze.real_h - 2)
            if self.maze.is_walkable(rx, ry) and abs(rx - p1_x) + abs(ry - p1_y) > 10:
                p2_x, p2_y = rx, ry
                break
            attempts += 1
        if attempts == 100:
            p2_x, p2_y = self.maze.real_w - 2, self.maze.real_h - 2  # Fallback, але перевір
            while not self.maze.is_walkable(p2_x, p2_y):
                p2_x -= 1
                p2_y -= 1
        print(f"[Spawn] Player 2 at: {p2_x}, {p2_y}")

        self.coins = CoinWrapper(self.maze)
        floor_count = self.map_data.count(0)
        self.coins.spawn(max(5, int(floor_count * 0.1)))

        if self.game_mode == "EvE":
            self.player1 = Enemy(p1_x, p1_y, self.assets, self.maze, self.coins)
        else:
            self.player1 = Player(p1_x, p1_y, self.assets, "WASD", self.maze, self.coins)

        if self.game_mode == "PvP":
            self.player2 = Player(p2_x, p2_y, self.assets, "ARROWS", self.maze, self.coins)
        else:
            self.player2 = Enemy(p2_x, p2_y, self.assets, self.maze, self.coins)

    def update(self, keys):



        if self.player1:
            # Перевіряємо прапорець is_bot (безпечніше, ніж isinstance)
            if getattr(self.player1, 'is_bot', False):
                self.player1.update()  # Бот думає сам
            else:
                self.player1.update(keys)  # Людина керується клавішами


        if self.player2:
            if getattr(self.player2, 'is_bot', False):
                self.player2.update()
            else:
                self.player2.update(keys)




        active_coins = self.coins.get_active_coins_list()
        return len(active_coins) > 0

    def draw(self, surface1, surface2):



        if self.player1:
            self._draw_view(surface1, self.player1)


        if self.player2:
            self._draw_view(surface2, self.player2)
        else:

            surface2.fill((0, 0, 0))

    def _draw_view(self, surface, focus_target):

        surface.fill((30, 30, 45))


        half_w = surface.get_width() // 2
        half_h = surface.get_height() // 2


        cam_x = (focus_target.x * CELL_SIZE) - half_w
        cam_y = (focus_target.y * CELL_SIZE) - half_h

        floor_img = self.assets.get_image('floor')

        rw = self.maze.real_w
        rh = self.maze.real_h

        for y in range(rh):
            for x in range(rw):

                screen_x = x * CELL_SIZE - cam_x
                screen_y = y * CELL_SIZE - cam_y


                if -CELL_SIZE <= screen_x <= surface.get_width() and -CELL_SIZE <= screen_y <= surface.get_height():


                    surface.blit(floor_img, (screen_x, screen_y))


                    idx = y * rw + x

                    if idx < len(self.map_data) and self.map_data[idx] == 1:
                        tex_idx = self.texture_data[idx] if idx < len(self.texture_data) else 0
                        wall_img = self.assets.get_wall_texture(tex_idx)
                        surface.blit(wall_img, (screen_x, screen_y))


        active_coins = self.coins.get_active_coins_list()
        for c in active_coins:
            cx = c['x'] * CELL_SIZE - cam_x
            cy = c['y'] * CELL_SIZE - cam_y
            if -CELL_SIZE < cx < surface.get_width() and -CELL_SIZE < cy < surface.get_height():
                img = self.assets.get_coin_texture(c['type'])
                surface.blit(img, (cx, cy))

        focus_target.draw(surface, cam_x, cam_y)

    def load_save(self, save_data):


        self.curr_w = save_data['map']['w']
        self.curr_h = save_data['map']['h']
        self.seed = save_data['map']['seed']
        self.game_mode = save_data['mode']


        self._init_level()


        p1_data = save_data['p1']
        self.player1.x = float(p1_data['x'])
        self.player1.y = float(p1_data['y'])
        self.player1.score = p1_data['score']

        if self.player2:
            p2_data = save_data['p2']
            self.player2.x = float(p2_data['x'])
            self.player2.y = float(p2_data['y'])
            self.player2.score = p2_data['score']


        self.coins.clearCoins()

        for coin in save_data.get('coins', []):
            self.coins.addCoin(
                coin['x'],
                coin['y'],
                coin['type'],
                coin['value'],
                True  # active
            )

        print(f"[GAME] Save loaded: {save_data['timestamp']} | Mode: {self.game_mode} | Seed: {self.seed}")