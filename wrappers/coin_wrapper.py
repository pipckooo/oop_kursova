import ctypes

from .dll_loader import lib, IntArray

class CoinWrapper:
    def __init__(self, maze_wrapper):
        lib.Coins_new.restype = ctypes.c_void_p
        lib.Coins_new.argtypes = [ctypes.c_void_p]

        lib.Coins_spawn.argtypes = [ctypes.c_void_p, ctypes.c_int]
        lib.Coins_spawn.restype = None

        lib.Coins_checkCollection.restype = ctypes.c_int
        lib.Coins_checkCollection.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

        lib.Coins_getData.restype = ctypes.POINTER(IntArray)
        lib.Coins_getData.argtypes = [ctypes.c_void_p]

        lib.Coins_clear.argtypes = [ctypes.c_void_p]
        lib.Coins_clear.restype = None

        lib.Coins_addCoin.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool]
        lib.Coins_addCoin.restype = None

        self.obj = lib.Coins_new(maze_wrapper.obj)

    def spawn(self, count):
        lib.Coins_spawn(self.obj, count)

    def check_collection(self, px, py):
        return lib.Coins_checkCollection(self.obj, px, py)

    def get_active_coins_list(self):
        ptr = lib.Coins_getData(self.obj)
        if not ptr:
            return []

        try:
            total_size = ptr.contents.size
            raw = [ptr.contents.data[i] for i in range(total_size)]
            lib.Free_array(ptr)

            coins = []
            count = raw[0]
            idx = 1
            for _ in range(count):
                if idx + 2 < len(raw):
                    coins.append({'x': raw[idx], 'y': raw[idx + 1], 'type': raw[idx + 2]})
                    idx += 3
            return coins
        except Exception as e:
            print(f"Error parsing coins: {e}")
            return []

    def clearCoins(self):
        lib.Coins_clear(self.obj)

    def addCoin(self, x, y, type_, value, active):
        lib.Coins_addCoin(self.obj, x, y, type_, value, active)