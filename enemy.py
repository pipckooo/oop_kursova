import pygame
from config import CELL_SIZE


class Enemy:
    def __init__(self, x, y, assets, maze_wrapper, coin_wrapper):
        self.x = x
        self.y = y
        self.is_bot = True
        self.score = 0

        # Графіка
        self.assets = assets
        self.img_idle = assets.get_image('p2_idle')
        self.img_move_list = assets.get_image('p2_move')

        self.frame_index = 0
        self.animation_speed = 0.15
        self.is_moving = False

        # Логіка
        self.maze = maze_wrapper
        self.coins = coin_wrapper
        self.path = []
        self.move_delay = 150
        self.last_move_time = 0

    def update(self):
        self.is_moving = False

        if not self._is_move_cooldown_over():
            return

        # Якщо шляху немає — шукаємо ціль
        if not self.path:
            self._find_new_target()

        # Якщо шлях з'явився — йдемо
        if self.path:
            self._step_forward()
        else:
            # DEBUG: Якщо бот стоїть, чому?
            # Розкоментуй, якщо хочеш бачити спам у консолі
            # print(f"[Bot] Standing at {self.x},{self.y}. Path is empty.")
            pass

    def _find_new_target(self):
        # 1. Отримуємо список монет
        active_coins = self.coins.get_active_coins_list()

        if not active_coins:
            print("[Bot] No active coins found on map!")
            return

            # 2. Шукаємо найближчу
        target = self._get_nearest_coin(active_coins)

        if target:
            # 3. Шукаємо шлях
            # print(f"[Bot] Calculate path: {self.x},{self.y} -> {target['x']},{target['y']}")
            found_path = self.maze.find_path(self.x, self.y, target['x'], target['y'])

            if found_path:
                self.path = found_path
                # Видаляємо поточну точку (щоб не топтатися на місці)
                if len(self.path) > 0:
                    self.path.pop(0)
                # print(f"[Bot] Path found! Length: {len(self.path)}")
            else:
                print(f"[Bot] Pathfinding failed to {target['x']},{target['y']} (Walls?)")

    def _get_nearest_coin(self, coins_list):
        nearest = None
        min_dist = float('inf')
        for c in coins_list:
            dist = abs(self.x - c['x']) + abs(self.y - c['y'])
            if dist < min_dist:
                min_dist = dist
                nearest = c
        return nearest

    def _step_forward(self):
        if not self.path: return

        next_step = self.path.pop(0)
        self.x = next_step[0]
        self.y = next_step[1]

        self.is_moving = True
        self.last_move_time = pygame.time.get_ticks()

        # Збір монет
        if self.coins:
            val = self.coins.check_collection(self.x, self.y)
            if val > 0:
                print(f"[Bot] Coin collected! Score +{val}")
                self.score += val

    def _is_move_cooldown_over(self):
        return pygame.time.get_ticks() - self.last_move_time > self.move_delay

    def draw(self, surface, offset_x, offset_y):
        img = self.img_idle
        if self.is_moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.img_move_list):
                self.frame_index = 0
            img = self.img_move_list[int(self.frame_index)]

        screen_x = self.x * CELL_SIZE - offset_x
        screen_y = self.y * CELL_SIZE - offset_y

        if img:
            surface.blit(img, (screen_x, screen_y))