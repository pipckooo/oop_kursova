# assets.py
import pygame
import os
from config import CELL_SIZE


class AssetManager:
    def __init__(self):
        self._base_dir = os.path.dirname(os.path.abspath(__file__))
        self._assets_dir = os.path.join(self._base_dir, "assets")
        self._data = {}  # Інкапсульований словник

        # Гарантуємо, що Pygame ініціалізовано перед завантаженням (для fonts/images)
        if not pygame.get_init():
            pygame.init()

    def _load_img(self, subpath):
        """Внутрішній метод для безпечного завантаження зображень"""
        full_path = os.path.join(self._assets_dir, subpath)

        if not os.path.exists(full_path):
            print(f"[WARNING] Image not found: {subpath}. Using placeholder.")
            # Створюємо кольоровий квадрат як заглушку
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
            surf.fill((255, 0, 255))  # Маджента (щоб було видно помилку)
            return surf

        img = pygame.image.load(full_path).convert_alpha()
        return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))

    def load_all(self):
        """Завантажує всі ресурси гри"""

        # --- ГРАВЦІ ---
        self._data['p1_idle'] = self._load_img('player/idle.png')
        self._data['p1_move'] = [
            self._load_img('player/move_1.png'),
            self._load_img('player/move_2.png')
        ]
        self._data['p2_idle'] = self._load_img('enemy/idle.png')
        self._data['p2_move'] = [
            self._load_img('enemy/move_1.png'),
            self._load_img('enemy/move_2.png')
        ]

        # --- МОНЕТИ (Важливо для C++ CoinManager) ---
        # C++ генерує типи 0, 1, 2. Нам треба мінімум 3 картинки.
        coin_files = ['coins/coin_1.png', 'coins/coin_2.png', 'coins/coin_3.png']
        self._data['coins'] = [self._load_img(f) for f in coin_files]

        # --- ПІДЛОГА ---
        if os.path.exists(os.path.join(self._assets_dir, 'tiles/sand_1.png')):
            self._data['floor'] = self._load_img('tiles/sand_1.png')
        else:
            self._data['floor'] = self._load_img('tiles/ground_blue.png')

        # --- СТІНИ (Важливо для C++ MazeGenerator) ---
        walls = []

        # Завантажуємо рослини
        plants_dir = os.path.join(self._assets_dir, 'plants')
        if os.path.exists(plants_dir):
            for f in sorted(os.listdir(plants_dir)):  # sorted для стабільного порядку
                if f.endswith('.png'):
                    walls.append(self._load_img(f"plants/{f}"))

        # Завантажуємо камені
        stones_dir = os.path.join(self._assets_dir, 'stones')
        if os.path.exists(stones_dir):
            for f in sorted(os.listdir(stones_dir)):
                if f.endswith('.png'):
                    walls.append(self._load_img(f"stones/{f}"))

        # Якщо стін немає, додаємо хоча б одну (підлогу або заглушку), щоб не було ділення на нуль
        if not walls:
            walls.append(self._data['floor'])

        self._data['walls'] = walls

        # --- ЗВУКИ ---
        snd_dir = os.path.join(self._assets_dir, "sounds")
        c_path = os.path.join(snd_dir, "coin_sound.mp3")

        self._data['sfx_coin'] = None
        if os.path.exists(c_path):
            try:
                self._data['sfx_coin'] = pygame.mixer.Sound(c_path)
            except Exception as e:
                print(f"[ERROR] Failed to load sound: {e}")

        self._data['music_path'] = os.path.join(snd_dir, "Hallow Quest.mp3")

    # --- PUBLIC ACCESSORS (Getter Methods) ---
    # Це забезпечує абстракцію. Гра просить "дай стіну №5",
    # а менеджер сам розбирається, чи існує така стіна.

    def get_wall_texture(self, texture_index):
        """Безпечно повертає текстуру стіни за індексом з C++"""
        walls = self._data.get('walls', [])
        if not walls:
            return self._data['floor']  # Fallback

        # Використовуємо модуль, щоб уникнути виходу за межі масиву
        # Це захищає, якщо C++ згенерував індекс 10, а у нас тільки 5 картинок
        return walls[texture_index % len(walls)]

    def get_coin_texture(self, coin_type):
        """Безпечно повертає текстуру монети"""
        coins = self._data.get('coins', [])
        if not coins:
            return self._data['floor']  # Fallback
        return coins[coin_type % len(coins)]

    def get_image(self, key):
        return self._data.get(key)

    def get_music_path(self):
        return self._data.get('music_path')

    def play_coin_sound(self):
        if self._data.get('sfx_coin'):
            self._data['sfx_coin'].play()

    @property
    def wall_variants_count(self):
        """Потрібно для передачі в C++ функцію Maze_generateTextures"""
        return len(self._data.get('walls', []))