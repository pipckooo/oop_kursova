#player.py
import pygame
from config import CELL_SIZE


class Player:
    def __init__(self, x, y, assets, control_scheme, maze_wrapper, coin_wrapper):
        self.x = float(x)  # Використовуємо float для плавності
        self.y = float(y)
        self.assets = assets
        self.maze = maze_wrapper
        self.coins = coin_wrapper
        self.score = 0
        self.is_bot = False
        # Налаштування управління
        self.controls = control_scheme  # "WASD" або "ARROWS"
        self.speed = 0.15  # Швидкість руху (частина клітинки за кадр)

        # Анімація
        self.img_idle = assets.get_image('p1_idle')
        self.img_move_list = assets.get_image('p1_move')
        self.frame_index = 0
        self.is_moving = False
        self.facing_left = False

    def update(self, keys):  # <--- ТУТ БУЛА ПОМИЛКА (було без keys)
        dx, dy = 0, 0

        # Обробка клавіш
        if self.controls == "WASD":
            if keys[pygame.K_w]:
                dy = -1
            elif keys[pygame.K_s]:
                dy = 1
            if keys[pygame.K_a]:
                dx = -1
            elif keys[pygame.K_d]:
                dx = 1
        elif self.controls == "ARROWS":
            if keys[pygame.K_UP]:
                dy = -1
            elif keys[pygame.K_DOWN]:
                dy = 1
            if keys[pygame.K_LEFT]:
                dx = -1
            elif keys[pygame.K_RIGHT]:
                dx = 1

        self.is_moving = (dx != 0 or dy != 0)

        if self.is_moving:
            move_speed = 0.2
            box_size = 0.3

            # --- РУХ ПО X ---
            if dx != 0:
                new_x = self.x + dx * move_speed

                # Центр + країв
                center_x = new_x + 0.5
                center_y = self.y + 0.5
                check_x = center_x + (box_size if dx > 0 else -box_size)

                top_chk = int(center_y - box_size)
                btm_chk = int(center_y + box_size)
                col_chk = int(check_x)

                # Тільки якщо вільно
                if self.maze.is_walkable(col_chk, top_chk) and \
                        self.maze.is_walkable(col_chk, btm_chk):
                    self.x = new_x

            # --- РУХ ПО Y ---
            if dy != 0:
                new_y = self.y + dy * move_speed

                center_x = self.x + 0.5
                center_y = new_y + 0.5
                check_y = center_y + (box_size if dy > 0 else -box_size)

                left_chk = int(center_x - box_size)
                rght_chk = int(center_x + box_size)
                row_chk = int(check_y)

                # Тільки якщо вільно
                if self.maze.is_walkable(left_chk, row_chk) and \
                        self.maze.is_walkable(rght_chk, row_chk):
                    self.y = new_y

            # Жорсткі межі (щоб не вилетів за карту при лагах)
            margin = 1.1
            if self.x < margin: self.x = margin
            if self.x > self.maze.real_w - margin: self.x = self.maze.real_w - margin
            if self.y < margin: self.y = margin
            if self.y > self.maze.real_h - margin: self.y = self.maze.real_h - margin

            # Анімація
            if dx < 0: self.facing_left = True
            if dx > 0: self.facing_left = False

            self.frame_index += 0.2
            if self.frame_index >= len(self.img_move_list):
                self.frame_index = 0

            # Збір монет
            val = self.coins.check_collection(int(self.x + 0.5), int(self.y + 0.5))
            if val > 0:
                self.assets.play_coin_sound()
                self.score += val

    def _is_move_cooldown_over(self):
        return pygame.time.get_ticks() - self.last_move_time > self.move_delay

    def draw(self, surface, offset_x, offset_y):
        img = self.img_idle
        if self.is_moving:
            img = self.img_move_list[int(self.frame_index) % len(self.img_move_list)]

        if self.facing_left:
            img = pygame.transform.flip(img, True, False)

        screen_x = self.x * CELL_SIZE - offset_x
        screen_y = self.y * CELL_SIZE - offset_y

        surface.blit(img, (screen_x, screen_y))