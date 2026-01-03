import pygame
import ctypes
from config import *


class Coin:
    def __init__(self, x, y, coin_type, image):
        self.x = x
        self.y = y
        self.type=coin_type
        self.image = image
        self.animation_offset=0


    def draw(self, surface, cam_x, cam_y):

        if self.image:
             screen_x = self.x * CELL_SIZE - cam_x
             screen_y = self.y * CELL_SIZE - cam_y
             surface.blit(self.image, (screen_x, screen_y))
        else:
            rect=pygame.Rect(
                self.x * CELL_SIZE - cam_x,
                self.y * CELL_SIZE - cam_y,
                CELL_SIZE - 20, CELL_SIZE - 20)


            color=(255,215,0) if self.type == 0 else (192,192,192)
            pygame.draw.ellipse(surface, color, rect)

    @staticmethod
    def setup_c_signatures(lib):


        # --- COIN ACTIONS ---
        lib.Maze_spawnCoins.argtypes = [ctypes.c_void_p, ctypes.c_int]
        lib.Maze_clearCoins.argtypes = [ctypes.c_void_p]

        lib.Maze_addCoin.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_bool
        ]

        # --- COIN QUERIES ---
        lib.Maze_getCoinsData.argtypes = [ctypes.c_void_p]
        lib.Maze_getCoinsData.restype = ctypes.POINTER(ctypes.c_int)

        lib.Maze_checkCollection.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        lib.Maze_checkCollection.restype = ctypes.c_int

        lib.Maze_hasCoins.argtypes = [ctypes.c_void_p]
        lib.Maze_hasCoins.restype = ctypes.c_bool

        # Legacy support (на всяк випадок)
        try:
            lib.Maze_getCoins.argtypes = [ctypes.c_void_p, ctypes.c_int]
            lib.Maze_getCoins.restype = ctypes.POINTER(ctypes.c_int)
        except AttributeError:
            pass