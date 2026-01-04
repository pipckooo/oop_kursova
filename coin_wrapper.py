import ctypes
import os




if os.name == 'nt':
    lib_path = './MazeCore.dll'


# Завантаження DLL
try:
    lib = ctypes.CDLL(lib_path)
except OSError as e:
    print(f"ERROR: Could not load {lib_path}. ")
    raise e



class CoinWrapper:
    def __init__(self, maze_wrapper):
        self.obj = lib.Coins_new(maze_wrapper.obj)

    def spawn(self, count):
        lib.Coins_spawn(self.obj, count)

    def check_collection(self, px, py):
        # Пряма передача (X, Y)
        return lib.Coins_checkCollection(self.obj, px, py)

    def get_active_coins_list(self):
        ptr = lib.Coins_getData(self.obj)
        # ДОДАЙ ПЕРЕВІРКУ НА NULL
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
                    cx = raw[idx]
                    cy = raw[idx + 1]
                    ctype = raw[idx + 2]
                    coins.append({'x': cx, 'y': cy, 'type': ctype})
                    idx += 3
            return coins
        except Exception as e:
            print(f"Error parsing coins: {e}")
            return []

    def clearCoins(self):

        # Потрібно додати експорт в C++: Coins_clear(CoinManager* c)
        lib.Coins_clear(self.obj)

    def addCoin(self, x, y, type_, value, active):

        # Потрібно додати експорт в C++: Coins_addCoin(CoinManager* c, int x, int y, int type, int value, bool active)
        lib.Coins_addCoin(self.obj, x, y, type_, value, 1 if active else 0)