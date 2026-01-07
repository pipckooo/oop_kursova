# wrappers/enemy_wrapper.py
import ctypes
from .dll_loader import lib, FloatArray


lib.Enemies_new.restype = ctypes.c_void_p
lib.Enemies_new.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

lib.Enemies_spawn.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
lib.Enemies_update.argtypes = [ctypes.c_void_p]

lib.Enemies_getData.restype = ctypes.POINTER(FloatArray)
lib.Enemies_getData.argtypes = [ctypes.c_void_p]

lib.Enemies_free.argtypes = [ctypes.c_void_p]


class EnemyWrapper:
    def __init__(self, maze_wrapper, coin_wrapper):

        self.obj = lib.Enemies_new(maze_wrapper.obj, coin_wrapper.obj)

    def spawn(self, x, y):
        lib.Enemies_spawn(self.obj, x, y)

    def update(self):

        lib.Enemies_update(self.obj)

    def get_data(self):

        ptr = lib.Enemies_getData(self.obj)
        if not ptr:
            return []

        try:
            total_size = ptr.contents.size
            raw = [ptr.contents.data[i] for i in range(total_size)]

            lib.Free_float_array(ptr)

            enemies = []
            count = int(raw[0])

            idx = 1
            for _ in range(count):
                if idx + 3 < len(raw):
                    e_id = int(raw[idx])
                    ex = raw[idx + 1]
                    ey = raw[idx + 2]
                    escore = int(raw[idx + 3])

                    enemies.append({'id': e_id, 'x': ex, 'y': ey, 'score': escore})
                    idx += 4
            return enemies
        except Exception as e:
            print(f"Error parsing enemies: {e}")
            return []

    def __del__(self):

        if hasattr(self, 'obj') and self.obj:
            lib.Enemies_free(self.obj)