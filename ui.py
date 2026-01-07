# ui.py
import pygame
from config import *


class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 24)
        self.font_mono = pygame.font.SysFont("Courier New", 20, bold=True)  # Для звіту

    def draw_button(self, text, cx, cy, mouse_pos, width=300):
        rect = pygame.Rect(0, 0, width, 50)
        rect.center = (cx, cy)
        color = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)

        txt = self.font_small.render(text, True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=rect.center))
        return rect

    def draw_volume_slider(self, cx, cy, volume, width=300, height=10):
        txt = self.font_small.render(f"VOLUME: {int(volume * 100)}%", True, WHITE)
        self.screen.blit(txt, (cx - width // 2, cy - 30))
        slider_rect = pygame.Rect(0, 0, width, 30)
        slider_rect.center = (cx, cy)
        bar_bg = pygame.Rect(cx - width // 2, cy - height // 2, width, height)
        pygame.draw.rect(self.screen, (100, 100, 100), bar_bg, border_radius=5)
        fill_width = int(width * volume)
        bar_fill = pygame.Rect(cx - width // 2, cy - height // 2, fill_width, height)
        pygame.draw.rect(self.screen, TEXT_GOLD, bar_fill, border_radius=5)
        handle_x = cx - width // 2 + fill_width
        pygame.draw.circle(self.screen, WHITE, (handle_x, cy), 12)
        return slider_rect

    def draw_main_menu(self, current_size):
        self.screen.fill(UI_BG)
        title = self.font_big.render("MAZE RUNNER", True, TEXT_GOLD)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 50))
        mp = pygame.mouse.get_pos()
        cx = SCREEN_W // 2

        b1 = self.draw_button("GAME MODES", cx, 180, mp)
        b2 = self.draw_button("SETTINGS", cx, 250, mp)
        b3 = self.draw_button(f"SIZE: {current_size}", cx, 320, mp)
        b4 = self.draw_button("LOAD GAME", cx, 390, mp)
        b5 = self.draw_button("EXIT", cx, 460, mp)
        return b1, b2, b3, b4, b5

    def draw_modes_menu(self):
        self.screen.fill(UI_BG)
        title = self.font_big.render("SELECT MODE", True, WHITE)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 80))
        mp = pygame.mouse.get_pos()
        cx = SCREEN_W // 2
        b1 = self.draw_button("HUMAN vs HUMAN", cx, 200, mp)
        b2 = self.draw_button("HUMAN vs BOT", cx, 270, mp)
        b3 = self.draw_button("BOT vs BOT", cx, 340, mp)
        b_back = self.draw_button("BACK", cx, 450, mp)
        return b1, b2, b3, b_back

    def draw_settings_menu(self, volume):
        self.screen.fill(UI_BG)
        title = self.font_big.render("SETTINGS", True, WHITE)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 80))
        mp = pygame.mouse.get_pos()
        cx = SCREEN_W // 2
        slider = self.draw_volume_slider(cx, 250, volume, width=400)
        btn_back = self.draw_button("BACK TO MENU", cx, 500, mp)
        return slider, btn_back

    def draw_load_menu(self, saves, scroll_y):
        self.screen.fill(UI_BG)
        title = self.font_big.render("SELECT SAVE", True, WHITE)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 50))
        mp = pygame.mouse.get_pos()
        cx = SCREEN_W // 2

        if not saves:
            t = self.font_small.render("No saves found", True, (150, 150, 150))
            self.screen.blit(t, (cx - t.get_width() // 2, 200))
            btn_back = self.draw_button("BACK", cx, 550, mp)
            return btn_back, []

        visible_items = 5
        start_y = 150
        visible_saves = saves[scroll_y: scroll_y + visible_items]

        buttons = []
        for i, s in enumerate(visible_saves):
            label = f"{s['timestamp']}  [{s['map']['w']}x{s['map']['h']}]"
            rect = self.draw_button(label, cx, start_y + i * 70, mp, 450)
            buttons.append(rect)

        if len(saves) > visible_items:
            bar_x = cx + 240
            bar_y = start_y - 25
            bar_h = visible_items * 70
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, 10, bar_h), border_radius=5)
            thumb_h = max(20, bar_h / (len(saves) / visible_items))
            thumb_y = bar_y + (scroll_y / len(saves)) * bar_h
            pygame.draw.rect(self.screen, TEXT_GOLD, (bar_x, thumb_y, 10, thumb_h), border_radius=5)

        btn_back = self.draw_button("BACK", cx, 550, mp)
        return btn_back, buttons

    def draw_save_options(self, save_data):
        self.screen.fill(UI_BG)

        title = self.font_big.render("SAVE OPTIONS", True, TEXT_GOLD)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 80))

        # Інфо про сейв
        info_text = f"Selected: {save_data['timestamp']}"
        info_surf = self.font_small.render(info_text, True, (200, 200, 200))
        self.screen.blit(info_surf, (SCREEN_W // 2 - info_surf.get_width() // 2, 150))

        mp = pygame.mouse.get_pos()
        cx = SCREEN_W // 2

        b_resume = self.draw_button("RESUME GAME", cx, 250, mp)
        b_report = self.draw_button("ANALYZE / REPORT", cx, 320, mp)
        b_back = self.draw_button("BACK", cx, 460, mp)

        return b_resume, b_report, b_back

    def draw_report_view(self, report_lines):
        self.screen.fill((30, 30, 30))

        # Заголовок
        title = self.font_big.render("GAME REPORT", True, WHITE)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 40))

        start_y = 120
        for line in report_lines:
            txt_surf = self.font_mono.render(line, True, (200, 255, 200))

            self.screen.blit(txt_surf, (SCREEN_W // 2 - 200, start_y))
            start_y += 30

        mp = pygame.mouse.get_pos()
        cx = SCREEN_W // 2

        b_print = self.draw_button("PRINT TO FILE (.txt)", cx, 500, mp, width=350)
        b_back = self.draw_button("BACK", cx, 570, mp)

        return b_print, b_back


    def draw_pause_menu(self, volume):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        title = self.font_big.render("PAUSED", True, WHITE)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 80))
        mp = pygame.mouse.get_pos()
        cx = SCREEN_W // 2
        b1 = self.draw_button("RESUME", cx, 200, mp)
        b2 = self.draw_button("SAVE GAME", cx, 270, mp)
        slider = self.draw_volume_slider(cx, 350, volume)
        b4 = self.draw_button("MAIN MENU", cx, 430, mp)
        return b1, b2, slider, b4


    def draw_game_over(self, s1, s2):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        if s1 > s2:
            txt = self.font_big.render("RABBIT WINS!", True, (100, 255, 100))
        elif s2 > s1:
            txt = self.font_big.render("MOUSE WINS!", True, (100, 100, 255))
        else:
            txt = self.font_big.render("DRAW!", True, WHITE)
        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        self.screen.blit(txt, (cx - txt.get_width() // 2, cy - 100))
        hint = self.font_small.render("[ENTER] Play Again   [ESC] Menu", True, WHITE)
        self.screen.blit(hint, (cx - hint.get_width() // 2, cy - 30))
        mp = pygame.mouse.get_pos()
        b_save = self.draw_button("SAVE RESULT", cx, cy + 50, mp)
        return b_save