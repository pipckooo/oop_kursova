# storage.py
import json
import os
from datetime import datetime

SAVE_FILE = "saves.json"


class GameStorage:
    @staticmethod
    def get_all_saves():
        if not os.path.exists(SAVE_FILE):
            return []
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                # Сортуємо за часом (найновіші зверху), якщо раптом порядок збився
                return data if isinstance(data, list) else []
        except:
            return []

    @staticmethod
    def add_save(session):
        saves = GameStorage.get_all_saves()

        # --- АДАПТАЦІЯ ПІД C++ ---
        # Монети знаходяться в пам'яті C++. Нам треба їх дістати через Wrapper.
        serializable_coins = []

        # Перевіряємо, чи існує обгортка монет у сесії
        if session.coins:
            # Отримуємо список словників [{'x':1, 'y':2, 'type':0}, ...] з C++
            active_coins_list = session.coins.get_active_coins_list()

            for c in active_coins_list:
                serializable_coins.append({
                    'x': c['x'],
                    'y': c['y'],
                    'type': c['type'],
                    'value': (c['type'] + 1) * 10
                })

        new_save = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": session.game_mode,

            # Зберігаємо SEED. Цього достатньо, щоб відтворити стіни лабіринту.
            "map": {
                "w": session.curr_w,
                "h": session.curr_h,
                "seed": session.seed
            },

            "p1": {
                "x": int(session.player1.x),
                "y": int(session.player1.y),
                "score": session.player1.score
            },

            # p2 може бути None, якщо гра ще не ініціалізована повністю, але зазвичай він є
            "p2": {
                "x": int(session.player2.x),
                "y": int(session.player2.y),
                "score": session.player2.score
            } if session.player2 else {"x": 0, "y": 0, "score": 0},

            "coins": serializable_coins
        }

        # Додаємо на початок списку
        saves.insert(0, new_save)

        # Обмежуємо кількість збережень (наприклад, 10 останніх)
        if len(saves) > 10:
            saves.pop()

        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(saves, f, indent=4)
        except Exception as e:
            print(f"Error saving game: {e}")