import pygame
import random


class Enemy:
    def __init__(self, x, y, assets, maze_wrapper, coin_wrapper):
        self.grid_x = int(x)
        self.grid_y = int(y)
        self.x = float(x)
        self.y = float(y)
        self.is_bot = True
        self.score = 0
        self.assets = assets
        self.img_idle = assets.get_image('p2_idle')
        self.img_move_list = assets.get_image('p2_move')
        self.frame_index = 0
        self.animation_speed = 0.25
        self.facing_left = False
        self.is_moving = False

        self.maze = maze_wrapper
        self.coins = coin_wrapper

        # DFS логіка
        self.visited = set()
        self.path_stack = []
        self.current_target = None
        self.move_progress = 0.0

    def update(self):

        val = self.coins.check_collection(self.grid_x, self.grid_y)
        if val > 0:
            self.score += val
            self.assets.play_coin_sound()


        if self.current_target:
            self.move_progress += 0.15
            if self.move_progress >= 1.0:
                self.grid_x, self.grid_y = self.current_target
                self.x, self.y = float(self.grid_x), float(self.grid_y)
                self.current_target = None
                self.move_progress = 0.0
                self.is_moving = False
            else:
                dx, dy = self.current_target[0] - self.grid_x, self.current_target[1] - self.grid_y
                self.x = self.grid_x + dx * self.move_progress
                self.y = self.grid_y + dy * self.move_progress
                self.is_moving = True
                self.facing_left = dx < 0
                self.frame_index += self.animation_speed
                if self.frame_index >= len(self.img_move_list):
                    self.frame_index = 0
                return


        self._dfs_step()

    def _dfs_step(self):
        self.visited.add((self.grid_x, self.grid_y))


        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if self.maze.is_walkable(nx, ny) and (nx, ny) not in self.visited:

                if self._has_coin(nx, ny):

                    self.path_stack.append((self.grid_x, self.grid_y))
                    self.current_target = (nx, ny)
                    return


        for dx, dy in directions:
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if self.maze.is_walkable(nx, ny) and (nx, ny) not in self.visited:
                self.path_stack.append((self.grid_x, self.grid_y))
                self.current_target = (nx, ny)
                return


        if self.path_stack:
            prev_x, prev_y = self.path_stack.pop()
            self.current_target = (prev_x, prev_y)
        else:

            self.visited.clear()

    def _has_coin(self, x, y):

        active_coins = self.coins.get_active_coins_list()
        for coin in active_coins:
            if coin['x'] == x and coin['y'] == y:
                return True
        return False

    def draw(self, surface, cam_x, cam_y):
        from config import CELL_SIZE
        screen_x = self.x * CELL_SIZE - cam_x
        screen_y = self.y * CELL_SIZE - cam_y

        if self.is_moving and self.img_move_list:
            img = self.img_move_list[int(self.frame_index) % len(self.img_move_list)]
        else:
            img = self.img_idle

        if self.facing_left:
            img = pygame.transform.flip(img, True, False)

        surface.blit(img, (screen_x, screen_y))