import ctypes
import os


class GameEngine:
    def __init__(self, w, h, enemy_count, coin_count):
        # Завантаження бібліотеки
        dll_path = os.path.join(os.path.dirname(__file__), "MazeCore.dll")
        self.lib = ctypes.CDLL(dll_path)

        # Опис сигнатур функцій C++
        self.lib.InitGame.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.lib.UpdateGame.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.UpdateGame.restype = ctypes.c_int
        self.lib.GetRenderData.restype = ctypes.POINTER(ctypes.c_int)
        self.lib.GetMapData.restype = ctypes.POINTER(ctypes.c_int)

        # Зберігаємо розміри
        self.real_w = w * 2 + 1
        self.real_h = h * 2 + 1

        # Ініціалізація (seed = 42)
        self.lib.InitGame(w, h, 42, enemy_count, coin_count)

        # Отримуємо мапу один раз (вона не змінюється)
        ptr = self.lib.GetMapData()
        self.map_data = [ptr[i] for i in range(self.real_w * self.real_h)]

    def update(self, dx, dy):
        """ dx, dy: -1, 0 або 1 """
        return self.lib.UpdateGame(dx, dy)

    def get_render_state(self):
        ptr = self.lib.GetRenderData()
        idx = 0

        state = {}
        state['score'] = ptr[idx];
        idx += 1
        state['player'] = (ptr[idx] / 100.0, ptr[idx + 1] / 100.0);
        idx += 2

        # Вороги
        e_count = ptr[idx];
        idx += 1
        state['enemies'] = []
        for _ in range(e_count):
            state['enemies'].append((ptr[idx] / 100.0, ptr[idx + 1] / 100.0))
            idx += 2

        # Монети
        c_count = ptr[idx];
        idx += 1
        state['coins'] = []
        for _ in range(c_count):
            state['coins'].append({'x': ptr[idx], 'y': ptr[idx + 1], 'type': ptr[idx + 2]})
            idx += 3

        return state