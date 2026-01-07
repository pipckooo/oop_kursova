# game_session.py
import pygame
import random
from config import *
from wrappers.maze_wrapper import MazeWrapper
from wrappers.coin_wrapper import CoinWrapper
from wrappers.enemy_wrapper import EnemyWrapper
from player import Player
from enemy import EnemyRenderer


class GameSession:
    def __init__(self, game_mode, difficulty, assets):
        self.game_mode = game_mode
        self.difficulty = difficulty
        self.assets = assets
        self.enemy_manager = None
        self.enemy_renderer = EnemyRenderer(assets)
        self.player1 = None
        self.player2 = None


        if difficulty in MAP_SIZES:
            self.curr_w, self.curr_h = MAP_SIZES[difficulty]
        else:
            self.curr_w, self.curr_h = 25, 19

        self.start_new(self.curr_w, self.curr_h, game_mode)

    def start_new(self, w, h, mode):
        self.curr_w = w
        self.curr_h = h
        self.game_mode = mode
        self.seed = random.randint(0, 999999)
        self._init_level()

    def _init_level(self):
        # 1. Лабіринт
        self.maze = MazeWrapper(self.curr_w, self.curr_h)
        self.map_data = self.maze.generate(self.seed)

        # Текстури
        variants = getattr(self.assets, 'wall_variants_count', 1)
        self.texture_data = self.maze.generate_textures(variants)

        # 2. Монети
        self.coins = CoinWrapper(self.maze)
        floor_count = self.map_data.count(0)
        self.coins.spawn(max(5, int(floor_count * 0.1)))

        # 3. Менеджер ворогів (C++)
        # Важливо: видаляємо старий, якщо був
        self.enemy_manager = EnemyWrapper(self.maze, self.coins)

        # 4. Спавн
        rw, rh = self.maze.real_w, self.maze.real_h
        p1_x, p1_y = 1, 1
        p2_x, p2_y = rw - 2, rh - 2

        # Налаштування Player 1
        if self.game_mode == "EvE":
            self.player1 = None
            self.enemy_manager.spawn(p1_x, p1_y)
        else:
            self.player1 = Player(p1_x, p1_y, self.assets, "WASD", self.maze, self.coins)

        # Налаштування Player 2
        if self.game_mode == "PvP":
            self.player2 = Player(p2_x, p2_y, self.assets, "ARROWS", self.maze, self.coins)
        else:
            self.player2 = None
            self.enemy_manager.spawn(p2_x, p2_y)

        # ВИПРАВЛЕНИЙ РЯДОК ТУТ:
        print(f"[SESSION] Level started. Mode: {self.game_mode}, Size: {rw}x{rh}")



    def update(self, keys):
        if self.player1: self.player1.update(keys)
        if self.player2: self.player2.update(keys)

        if self.enemy_manager:
            self.enemy_manager.update()

        active_coins = self.coins.get_active_coins_list()
        return len(active_coins) > 0

    def get_scores(self):
        s1, s2 = 0, 0
        bots_data = self.enemy_manager.get_data() if self.enemy_manager else []

        if self.player1:
            s1 = self.player1.score
        elif len(bots_data) > 0:
            s1 = int(bots_data[0]['score'])

        if self.player2:
            s2 = self.player2.score
        else:

            idx = 1 if self.player1 is None else 0
            if len(bots_data) > idx:
                s2 = int(bots_data[idx]['score'])

        return s1, s2

    def draw(self, surface1, surface2):

        bots_data = []
        if self.enemy_manager:
            bots_data = self.enemy_manager.get_data()


        if self.player1:
            self._draw_view(surface1, self.player1, bots_data)
        elif len(bots_data) > 0:

            dummy = type('obj', (object,), {'x': bots_data[0]['x'], 'y': bots_data[0]['y'], 'draw': lambda *a: None})
            self._draw_view(surface1, dummy, bots_data)
        else:
            surface1.fill((0, 0, 0))

        if self.player2:
            self._draw_view(surface2, self.player2, bots_data)

        elif len(bots_data) > 1:
            dummy = type('obj', (object,), {'x': bots_data[1]['x'], 'y': bots_data[1]['y'], 'draw': lambda *a: None})
            self._draw_view(surface2, dummy, bots_data)
        elif len(bots_data) > 0 and self.player1:

            dummy = type('obj', (object,), {'x': bots_data[0]['x'], 'y': bots_data[0]['y'], 'draw': lambda *a: None})
            self._draw_view(surface2, dummy, bots_data)
        else:
            surface2.fill((0, 0, 0))

    def _draw_view(self, surface, focus_target, bots_data):
        surface.fill(BG_COLOR)

        half_w = surface.get_width() // 2
        half_h = surface.get_height() // 2

        tx = getattr(focus_target, 'x', 1)
        ty = getattr(focus_target, 'y', 1)

        cam_x = (tx * CELL_SIZE) - half_w
        cam_y = (ty * CELL_SIZE) - half_h

        floor_img = self.assets.get_image('floor')
        rw = self.maze.real_w
        rh = self.maze.real_h

        start_x = max(0, int(cam_x // CELL_SIZE))
        end_x = min(rw, int((cam_x + surface.get_width()) // CELL_SIZE) + 1)
        start_y = max(0, int(cam_y // CELL_SIZE))
        end_y = min(rh, int((cam_y + surface.get_height()) // CELL_SIZE) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * CELL_SIZE - cam_x
                screen_y = y * CELL_SIZE - cam_y

                if floor_img: surface.blit(floor_img, (screen_x, screen_y))

                idx = y * rw + x
                if idx < len(self.map_data) and self.map_data[idx] == 1:
                    tex_idx = self.texture_data[idx] if idx < len(self.texture_data) else 0
                    wall_img = self.assets.get_wall_texture(tex_idx)
                    if wall_img: surface.blit(wall_img, (screen_x, screen_y))

        active_coins = self.coins.get_active_coins_list()
        for c in active_coins:
            cx = c['x'] * CELL_SIZE - cam_x
            cy = c['y'] * CELL_SIZE - cam_y
            if -CELL_SIZE < cx < surface.get_width() and -CELL_SIZE < cy < surface.get_height():
                img = self.assets.get_coin_texture(c['type'])
                if img: surface.blit(img, (cx, cy))

        for bot in bots_data:
            self.enemy_renderer.draw(surface, bot['x'], bot['y'], cam_x, cam_y)

        if hasattr(focus_target, 'draw') and callable(focus_target.draw):
            focus_target.draw(surface, cam_x, cam_y)

    def load_save(self, save_data):
        self.curr_w = save_data['map']['w']
        self.curr_h = save_data['map']['h']
        self.seed = save_data['map']['seed']
        self.game_mode = save_data['mode']

        self._init_level()

        self.coins.clearCoins()
        for c in save_data.get('coins', []):
            self.coins.addCoin(c['x'], c['y'], c['type'], c['value'], True)

        if self.player1:
            self.player1.x = save_data['p1']['x']
            self.player1.y = save_data['p1']['y']
            self.player1.score = save_data['p1']['score']

        if self.player2:
            self.player2.x = save_data['p2']['x']
            self.player2.y = save_data['p2']['y']
            self.player2.score = save_data['p2']['score']