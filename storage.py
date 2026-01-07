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
                return data if isinstance(data, list) else []
        except:
            return []

    @staticmethod
    def add_save(session):
        saves = GameStorage.get_all_saves()


        serializable_coins = []
        if session.coins:
            active_coins_list = session.coins.get_active_coins_list()
            for c in active_coins_list:
                serializable_coins.append({
                    'x': c['x'],
                    'y': c['y'],
                    'type': c['type'],
                    'value': (c['type'] + 1) * 10
                })


        bots_data = []
        if session.enemy_manager:
            bots_data = session.enemy_manager.get_data()


        if session.player1:
            p1_data = {
                "x": int(session.player1.x),
                "y": int(session.player1.y),
                "score": session.player1.score
            }
        elif len(bots_data) > 0:
            bot = bots_data[0]
            p1_data = {
                "x": int(bot['x']),
                "y": int(bot['y']),
                "score": int(bot['score'])
            }
        else:
            # Fallback (якщо щось пішло не так)
            p1_data = {"x": 1, "y": 1, "score": 0}


        if session.player2:
            p2_data = {
                "x": int(session.player2.x),
                "y": int(session.player2.y),
                "score": session.player2.score
            }
        else:

            bot_idx = 1 if session.player1 is None else 0

            if len(bots_data) > bot_idx:
                bot = bots_data[bot_idx]
                p2_data = {
                    "x": int(bot['x']),
                    "y": int(bot['y']),
                    "score": int(bot['score'])
                }
            else:
                p2_data = {"x": 0, "y": 0, "score": 0}


        new_save = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": session.game_mode,
            "map": {
                "w": session.curr_w,
                "h": session.curr_h,
                "seed": session.seed
            },
            "p1": p1_data,
            "p2": p2_data,
            "coins": serializable_coins
        }


        saves.insert(0, new_save)
        if len(saves) > 10:
            saves.pop()

        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(saves, f, indent=4)
        except Exception as e:
            print(f"Error saving game: {e}")