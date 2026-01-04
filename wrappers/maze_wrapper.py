import ctypes

from .dll_loader import lib, IntArray

class MazeWrapper:
    def __init__(self, w, h):
        lib.Maze_new.restype = ctypes.c_void_p
        lib.Maze_new.argtypes = [ctypes.c_int, ctypes.c_int]

        lib.Maze_getRealWidth.restype = ctypes.c_int
        lib.Maze_getRealWidth.argtypes = [ctypes.c_void_p]

        lib.Maze_getRealHeight.restype = ctypes.c_int
        lib.Maze_getRealHeight.argtypes = [ctypes.c_void_p]

        lib.Maze_generate.restype = ctypes.POINTER(IntArray)
        lib.Maze_generate.argtypes = [ctypes.c_void_p, ctypes.c_int]

        lib.Maze_generateTextures.restype = ctypes.POINTER(IntArray)
        lib.Maze_generateTextures.argtypes = [ctypes.c_void_p, ctypes.c_int]

        lib.Maze_isWalkable.restype = ctypes.c_bool
        lib.Maze_isWalkable.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

        lib.Maze_findPath.restype = ctypes.POINTER(IntArray)
        lib.Maze_findPath.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

        self.obj = lib.Maze_new(w, h)
        self.real_w = lib.Maze_getRealWidth(self.obj)
        self.real_h = lib.Maze_getRealHeight(self.obj)

        print(f"MAZE WRAPPER: Logic {w}x{h} -> Real {self.real_w}x{self.real_h}")

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
            if ptr:
                lib.Free_array(ptr)
            return []

        raw_data = [ptr.contents.data[i] for i in range(ptr.contents.size)]
        lib.Free_array(ptr)

        path = []
        for i in range(0, len(raw_data), 2):
            path.append((raw_data[i], raw_data[i + 1]))
        return path