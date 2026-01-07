#wrapper.py
import ctypes
import os
from wrappers.coin_wrapper import CoinWrapper
from int_array import IntArray


if os.name == 'nt':
    lib_path = './MazeCore.dll'



try:
    lib = ctypes.CDLL(lib_path)
except OSError as e:
    print(f"ERROR: Could not load {lib_path}. ")
    raise e






lib.Maze_new.restype = ctypes.c_void_p
lib.Maze_new.argtypes = [ctypes.c_int, ctypes.c_int]


lib.Maze_getRealWidth.restype = ctypes.c_int
lib.Maze_getRealWidth.argtypes = [ctypes.c_void_p]

lib.Maze_getRealHeight.restype = ctypes.c_int
lib.Maze_getRealHeight.argtypes = [ctypes.c_void_p]

lib.Coins_clear.argtypes = [ctypes.c_void_p]
lib.Coins_clear.restype = None

lib.Coins_addCoin.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool]
lib.Coins_addCoin.restype = None

lib.Maze_generate.restype = ctypes.POINTER(IntArray)
lib.Maze_generate.argtypes = [ctypes.c_void_p, ctypes.c_int]

lib.Maze_generateTextures.restype = ctypes.POINTER(IntArray)
lib.Maze_generateTextures.argtypes = [ctypes.c_void_p, ctypes.c_int]

lib.Maze_isWalkable.restype = ctypes.c_bool
lib.Maze_isWalkable.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

lib.Maze_findPath.restype = ctypes.POINTER(IntArray)
lib.Maze_findPath.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

lib.Free_array.argtypes = [ctypes.POINTER(IntArray)]



class MazeWrapper:
    def __init__(self, w, h):

        self.obj = lib.Maze_new(w, h)


        self.real_w = lib.Maze_getRealWidth(self.obj)
        self.real_h = lib.Maze_getRealHeight(self.obj)

        print(f"WRAPPER: Initialized Maze. Logic: {w}x{h} -> Real: {self.real_w}x{self.real_h}")

    def generate(self, seed):
        ptr = lib.Maze_generate(self.obj, seed)

        data = [ptr.contents.data[i] for i in range(ptr.contents.size)]
        lib.Free_array(ptr)
        return data

    def generate_textures(self, variants):
        ptr = lib.Maze_generateTextures(self.obj, variants)
        data = [ptr.contents.data[i] for i in range(ptr.contents.size)]
        lib.Free_array(ptr)
        return data

    def is_walkable(self, x, y):

        if x < 0 or x >= self.real_w or y < 0 or y >= self.real_h:
            return False
        return lib.Maze_isWalkable(self.obj, x, y)

    def find_path(self, sx, sy, tx, ty):

        ptr = lib.Maze_findPath(self.obj, sx, sy, tx, ty)

        if not ptr or ptr.contents.size == 0:
            if ptr: lib.Free_array(ptr)
            return []


        raw_data = [ptr.contents.data[i] for i in range(ptr.contents.size)]
        lib.Free_array(ptr)

        path = []

        for i in range(0, len(raw_data), 2):
            x = raw_data[i]
            y = raw_data[i + 1]
            path.append((x, y))

        return path



lib.Coins_new.restype = ctypes.c_void_p
lib.Coins_new.argtypes = [ctypes.c_void_p]

lib.Coins_spawn.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.Coins_checkCollection.restype = ctypes.c_int

lib.Coins_checkCollection.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
lib.Coins_getData.restype = ctypes.POINTER(IntArray)
lib.Coins_getData.argtypes = [ctypes.c_void_p]


