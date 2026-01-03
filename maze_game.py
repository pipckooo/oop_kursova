import pygame
import sys
import os
from config import *
from ui import UI
from storage import GameStorage

# --- ВИПРАВЛЕННЯ 1: Імпортуємо нові класи ---
from assets import AssetManager
from reports import ReportManager
from game_session import GameSession


class MazeGame:
    def __init__(self):
        self._init_pygame()

        # --- ВИПРАВЛЕННЯ 2: Ініціалізуємо менеджер ресурсів ---
        self.assets = AssetManager()
        self.assets.load_all()  # Завантажуємо картинки та звуки

        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.ui = UI(self.screen)

        # Передаємо об'єкт менеджера в сесію
        self.session = GameSession(self.assets)

        self._init_state()
        self.init_music()

        # Реєстр станів
        self.state_handlers = {
            "MENU": self.handle_menu,
            "MODES": self.handle_modes,
            "SETTINGS": self.handle_settings,
            "LOAD": self.handle_load,
            "SAVE_OPTIONS": self.handle_save_options,
            "REPORT": self.handle_report,
            "GAME": self.handle_game,
            "PAUSE": self.handle_pause,
            "OVER": self.handle_game_over
        }

    def _init_pygame(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Maze Speedrun: Ultimate Edition")
        self.clock = pygame.time.Clock()
        self.surf1 = pygame.Surface((VIEW_W, VIEW_H))
        self.surf2 = pygame.Surface((VIEW_W, VIEW_W))

    def _init_state(self):
        self.state = "MENU"
        self.running = True
        self.volume = 0.5
        self.size_keys = ['SMALL', 'MEDIUM', 'LARGE']
        self.curr_size_idx = 1
        self.saves_cache = []
        self.scroll_offset = 0
        self.selected_save = None
        self.report_lines = []

    def init_music(self):
        # --- ВИПРАВЛЕННЯ 3: Отримуємо шлях до музики через метод ---
        music_path = self.assets.get_music_path()
        if music_path and os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                self.set_volume(self.volume)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Music Load Error: {e}")

    def set_volume(self, v):
        self.volume = max(0.0, min(1.0, v))
        pygame.mixer.music.set_volume(self.volume * 0.5)

        # Отримуємо об'єкт звуку через менеджер, щоб змінити гучність
        sfx = self.assets.get_image('sfx_coin')  # get_image повертає raw об'єкт з _data
        if sfx and isinstance(sfx, pygame.mixer.Sound):
            sfx.set_volume(self.volume)

    # MAIN LOOP
    def run(self):
        while self.running:
            self._process_system_events()

            handler = self.state_handlers.get(self.state)
            if handler:
                handler()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def _process_system_events(self):
        self.events = pygame.event.get()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pressed = pygame.mouse.get_pressed()[0]
        for e in self.events:
            if e.type == pygame.QUIT:
                self.running = False

    # HELPERS
    def _save_and_menu(self):
        GameStorage.add_save(self.session)
        self.state = "MENU"

    def _process_slider(self, slider_rect):
        if self.mouse_pressed and slider_rect:
            if slider_rect.collidepoint(self.mouse_pos) or \
                    (slider_rect.y < self.mouse_pos[1] < slider_rect.bottom and
                     slider_rect.x - 30 < self.mouse_pos[0] < slider_rect.right + 30):
                new_vol = (self.mouse_pos[0] - slider_rect.x) / slider_rect.width
                self.set_volume(new_vol)

    def _update_scroll(self, dy):
        self.scroll_offset -= dy
        max_scroll = max(0, len(self.saves_cache) - 5)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    # --- RENDER HELPERS (Visuals) ---
    def _render_split_screen(self):
        self.screen.blit(self.surf1, (0, 0))
        self.screen.blit(self.surf2, (VIEW_W, 0))
        pygame.draw.line(self.screen, WHITE, (VIEW_W, 0), (VIEW_W, VIEW_H), 4)

    def _render_hud(self):
        s1 = self.font.render(f"Rabbit: {self.session.player1.score}", True, TEXT_GOLD)

        # Перевірка на існування другого гравця (щоб уникнути помилок при завантаженні меню)
        if self.session.player2:
            lbl2 = "Bot" if self.session.player2.is_bot else "Mouse"
            s2 = self.font.render(f"{lbl2}: {self.session.player2.score}", True, TEXT_GOLD)
        else:
            s2 = self.font.render("", True, TEXT_GOLD)

        self.screen.blit(s1, (20, 20))
        self.screen.blit(s2, (VIEW_W + 20, 20))

    # GAME STATE
    def handle_game(self):
        self._input_game()
        self._logic_game()
        self._draw_game()

    def _input_game(self):
        for e in self.events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: self.state = "PAUSE"
                if e.key == pygame.K_z: self._save_and_menu()

    def _logic_game(self):
        keys = pygame.key.get_pressed()
        has_coins = self.session.update(keys)
        if not has_coins:
            self.state = "OVER"
            pygame.mixer.music.stop()

    def _draw_game(self):
        # 1. Малюємо світ у буфери
        self.session.draw(self.surf1, self.surf2)
        # 2. Компонуємо на екран
        self._render_split_screen()
        # 3. Інтерфейс
        self._render_hud()

    # PAUSE STATE
    def handle_pause(self):
        self._render_split_screen()
        ui_rects = self.ui.draw_pause_menu(self.volume)
        self._input_pause(ui_rects)

    def _input_pause(self, ui_rects):
        b_resume, b_save, slider_rect, b_menu = ui_rects

        self._process_slider(slider_rect)

        for e in self.events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = "GAME"

            if e.type == pygame.MOUSEBUTTONDOWN:
                if b_resume.collidepoint(self.mouse_pos):
                    self.state = "GAME"
                elif b_save.collidepoint(self.mouse_pos):
                    self._save_and_menu()
                elif b_menu.collidepoint(self.mouse_pos):
                    self.state = "MENU"

    # MENU STATE
    def handle_menu(self):
        buttons = self.ui.draw_main_menu(self.size_keys[self.curr_size_idx])
        for e in self.events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                self._on_menu_click(buttons)

    def _on_menu_click(self, buttons):
        b_play, b_sett, b_size, b_load, b_exit = buttons

        if b_play.collidepoint(self.mouse_pos):
            self.state = "MODES"
        elif b_sett.collidepoint(self.mouse_pos):
            self.state = "SETTINGS"
        elif b_size.collidepoint(self.mouse_pos):
            self.curr_size_idx = (self.curr_size_idx + 1) % 3
        elif b_load.collidepoint(self.mouse_pos):
            self.saves_cache = GameStorage.get_all_saves()
            self.scroll_offset = 0
            self.state = "LOAD"
        elif b_exit.collidepoint(self.mouse_pos):
            self.running = False

    # SETTINGS STATE
    def handle_settings(self):
        slider_rect, btn_back = self.ui.draw_settings_menu(self.volume)
        self._process_slider(slider_rect)

        for e in self.events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.collidepoint(self.mouse_pos):
                    self.state = "MENU"

    # LOAD STATE
    def handle_load(self):
        back_btn, save_rects = self.ui.draw_load_menu(self.saves_cache, self.scroll_offset)

        for e in self.events:
            if e.type == pygame.MOUSEWHEEL:
                self._update_scroll(e.y)

            if e.type == pygame.MOUSEBUTTONDOWN:
                self._on_load_click(back_btn, save_rects)

    def _on_load_click(self, back_btn, save_rects):
        if back_btn.collidepoint(self.mouse_pos):
            self.state = "MENU"
            return

        for i, rect in enumerate(save_rects):
            if rect.collidepoint(self.mouse_pos):
                idx = self.scroll_offset + i
                if idx < len(self.saves_cache):
                    self.selected_save = self.saves_cache[idx]
                    self.state = "SAVE_OPTIONS"

    # OTHER SIMPLE STATES
    def handle_modes(self):
        b1, b2, b3, b_back = self.ui.draw_modes_menu()
        for e in self.events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                w, h = MAP_SIZES[self.size_keys[self.curr_size_idx]]
                if b1.collidepoint(self.mouse_pos):
                    self.session.start_new(w, h, "PvP");
                    self.state = "GAME"
                elif b2.collidepoint(self.mouse_pos):
                    self.session.start_new(w, h, "PvE");
                    self.state = "GAME"
                elif b3.collidepoint(self.mouse_pos):
                    self.session.start_new(w, h, "EvE");
                    self.state = "GAME"
                elif b_back.collidepoint(self.mouse_pos):
                    self.state = "MENU"

    def handle_save_options(self):
        b_res, b_rep, b_back = self.ui.draw_save_options(self.selected_save)
        for e in self.events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if b_res.collidepoint(self.mouse_pos):
                    self.session.load_save(self.selected_save);
                    self.state = "GAME"
                elif b_rep.collidepoint(self.mouse_pos):
                    # --- ВИПРАВЛЕННЯ 4: Використовуємо клас ReportManager ---
                    self.report_lines = ReportManager.generate(self.selected_save)
                    self.state = "REPORT"
                elif b_back.collidepoint(self.mouse_pos):
                    self.state = "LOAD"

    def handle_report(self):
        b_print, b_back = self.ui.draw_report_view(self.report_lines)
        for e in self.events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if b_print.collidepoint(self.mouse_pos):
                    # --- ВИПРАВЛЕННЯ 4: Використовуємо клас ReportManager ---
                    ReportManager.save_to_file(self.report_lines)
                elif b_back.collidepoint(self.mouse_pos):
                    self.state = "SAVE_OPTIONS"

    def handle_game_over(self):
        # Безпечне отримання рахунку p2
        s2 = self.session.player2.score if self.session.player2 else 0
        b_save = self.ui.draw_game_over(self.session.player1.score, s2)

        for e in self.events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: self.state = "MENU"
                if e.key == pygame.K_RETURN:
                    self.session.start_new(self.session.curr_w, self.session.curr_h, self.session.game_mode)
                    self.state = "GAME"
            if e.type == pygame.MOUSEBUTTONDOWN and b_save.collidepoint(self.mouse_pos):
                self._save_and_menu()