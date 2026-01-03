import pygame
from config import CELL_SIZE


class Player:
    def __init__(self, x, y, assets, control_scheme, maze_wrapper, coin_wrapper=None):
        self.x = x
        self.y = y
        self.score = 0
        self.is_bot = False

        self.assets = assets
        self.prefix = 'p1' if control_scheme == 'WASD' else 'p2'

        self.img_idle = assets.get_image(f'{self.prefix}_idle')
        self.img_move_list = assets.get_image(f'{self.prefix}_move')

        self.frame_index = 0
        self.animation_speed = 0.15
        self.is_moving = False

        self.controls = control_scheme
        self.last_move_time = 0
        self.move_delay = 120

        self.maze = maze_wrapper
        self.coins = coin_wrapper

        # Запам'ятовуємо, чи дивиться гравець вліво (для віддзеркалення)
        self.facing_left = False

    def update(self, keys):
        if not self._is_move_cooldown_over():
            return

        self.is_moving = False
        dx, dy = self._get_input_direction(keys)

        if dx != 0 or dy != 0:
            # === ПРОСТА ЛОГІКА (ЯК У СТАРОМУ КОДІ) ===
            # Якщо йдемо вліво - ставимо прапорець flip = True
            if dx == -1:
                self.facing_left = True
            # Якщо йдемо вправо - ставимо прапорець flip = False
            elif dx == 1:
                self.facing_left = False

            # (Вгору/Вниз не змінюють орієнтацію ліво/право)

            target_x = self.x + dx
            target_y = self.y + dy
            self._try_move_human(target_x, target_y)

    def _try_move_human(self, tx, ty):
        if self.maze and not self.maze.is_walkable(tx, ty):
            return
        self._execute_move(tx, ty)

    def _execute_move(self, tx, ty):
        self.x = tx
        self.y = ty
        self.last_move_time = pygame.time.get_ticks()
        self.is_moving = True

        if self.coins:
            val = self.coins.check_collection(self.x, self.y)
            if val > 0:
                self.score += val
                if self.assets:
                    self.assets.play_coin_sound()

    def _get_input_direction(self, keys):
        dx, dy = 0, 0
        if self.controls == 'WASD':
            if keys[pygame.K_w]:
                dy = -1
            elif keys[pygame.K_s]:
                dy = 1
            elif keys[pygame.K_a]:
                dx = -1
            elif keys[pygame.K_d]:
                dx = 1
        elif self.controls == 'ARROWS':
            if keys[pygame.K_UP]:
                dy = -1
            elif keys[pygame.K_DOWN]:
                dy = 1
            elif keys[pygame.K_LEFT]:
                dx = -1
            elif keys[pygame.K_RIGHT]:
                dx = 1
        return dx, dy

    def _is_move_cooldown_over(self):
        return pygame.time.get_ticks() - self.last_move_time > self.move_delay

    def draw(self, surface, offset_x, offset_y):
        # 1. Вибір картинки
        img = self.img_idle
        if self.is_moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.img_move_list):
                self.frame_index = 0
            img = self.img_move_list[int(self.frame_index)]

        if not img: return

        # 2. ПРОСТЕ ВІДДЗЕРКАЛЕННЯ (FLIP) ЗАМІСТЬ ПОВОРОТУ (ROTATE)
        # pygame.transform.flip(surface, flip_x, flip_y)
        if self.facing_left:
            # Якщо дивимось вліво -> дзеркалимо по горизонталі
            img = pygame.transform.flip(img, True, False)

        # 3. Малювання (без складного центрування, бо розмір не змінився)
        screen_x = self.x * CELL_SIZE - offset_x
        screen_y = self.y * CELL_SIZE - offset_y

        surface.blit(img, (screen_x, screen_y))