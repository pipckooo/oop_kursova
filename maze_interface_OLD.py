import ctypes
import os
import sys

from coin_OLD import Coin



if sys.platform == "win32":
    # Ми на Windows
    DLL_NAME = "MazeCore.dll"
else:
    # Ми на Linux (Docker)
    # Linux любить префікс "lib" і розширення ".so"
    DLL_NAME = "libMazeCore.so"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DLL_PATH = os.path.join(BASE_DIR, DLL_NAME)


class MazeInterface:
    def __init__(self):
        self._load_library()
        self._setup_all_signatures()

    def _load_library(self):
        try:
            self.lib = ctypes.CDLL(DLL_PATH)
        except OSError:
            print(f"CRITICAL ERROR: {DLL_NAME} not found at {DLL_PATH}!")
            sys.exit()

    def _setup_all_signatures(self):
        self._setup_lifecycle()
        self._setup_generation()
        self._setup_collision()
        self._setup_pathfinding()
        Coin.setup_c_signatures(self.lib)

    # LIFECYCLE
    def _setup_lifecycle(self):
        self.lib.Maze_new.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.Maze_new.restype = ctypes.c_void_p
        self.lib.Maze_delete.argtypes = [ctypes.c_void_p]

    # GENERATION
    def _setup_generation(self):
        self.lib.Maze_setSeed.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.lib.Maze_generateAndGet.argtypes = [ctypes.c_void_p]
        self.lib.Maze_generateAndGet.restype = ctypes.POINTER(ctypes.c_int)

        # Генерація текстур
        try:
            self.lib.Maze_generateTextures.argtypes = [ctypes.c_void_p, ctypes.c_int]
            self.lib.Maze_generateTextures.restype = ctypes.POINTER(ctypes.c_int)
        except AttributeError:
            pass

        self.lib.Free_array.argtypes = [ctypes.POINTER(ctypes.c_int)]

    # COLLISION
    def _setup_collision(self):
        self.lib.Maze_isWalkable.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.lib.Maze_isWalkable.restype = ctypes.c_bool

    # PATHFINDING
    def _setup_pathfinding(self):
        self.lib.Maze_findPath.argtypes = [
            ctypes.c_void_p,  # <--- ВАЖЛИВО: c_void_p замість c_int
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int
        ]
        self.lib.Maze_findPath.restype = ctypes.POINTER(ctypes.c_int)




core_wrapper = MazeInterface()
core = core_wrapper.lib