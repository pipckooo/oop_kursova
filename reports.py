#reports.py
import os
from datetime import datetime
from wrapper import MazeWrapper  # Підключаємо нашу C++ обгортку


class ReportManager:


    @staticmethod
    def generate(save_data):
        lines = []
        lines.append("====== GAME REPORT ======")
        lines.append(f"Date: {save_data['timestamp']}")

        # Дані карти
        w = save_data['map']['w']
        h = save_data['map']['h']
        seed = save_data['map']['seed']

        lines.append(f"Map Logic Size: {w} x {h}")
        lines.append(f"Map Seed: {seed}")


        try:

            temp_maze = MazeWrapper(w, h)
            temp_maze.generate(seed)


            start_node = (1, 1)
            end_node = (temp_maze.real_w - 2, temp_maze.real_h - 2)

            path = temp_maze.find_path(start_node[0], start_node[1], end_node[0], end_node[1])
            optimal_steps = len(path) if path else 0

            lines.append(f"Optimal Path Length: {optimal_steps} steps")
            lines.append(f"Maze Complexity: {'High' if optimal_steps > 100 else 'Normal'}")


        except Exception as e:
            lines.append(f"[Analytics Error: {e}]")

        lines.append("-" * 25)


        s1 = save_data['p1']['score']

        s2 = save_data['p2']['score'] if 'p2' in save_data else 0

        lines.append(f"Player 1 Score: {s1}")
        lines.append(f"Player 2 Score: {s2}")
        lines.append("-" * 25)

        if s1 > s2:
            lines.append("WINNER: RABBIT")
        elif s2 > s1:
            lines.append("WINNER: MOUSE")
        else:
            lines.append("RESULT: DRAW")

        lines.append("=========================")
        return lines

    @staticmethod
    def save_to_file(lines):
        if not os.path.exists("reports"):
            os.makedirs("reports")

        filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, "w", encoding='utf-8') as f:
                for line in lines:
                    f.write(line + "\n")
            print(f"Report saved: {filename}")
        except Exception as e:
            print(f"Error saving report: {e}")