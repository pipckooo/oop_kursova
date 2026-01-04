# wrappers/dll_loader.py
import ctypes
import os

import os

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # піднімається на 2 рівні вгору
lib_path = os.path.join(project_dir, 'MazeCore.dll')

# Завантаження DLL
try:
    lib = ctypes.CDLL(lib_path)
except OSError as e:
    print(f"ERROR: Could not load {lib_path}. ")
    raise e

# Структура для масивів
class IntArray(ctypes.Structure):
    _fields_ = [("data", ctypes.POINTER(ctypes.c_int)), ("size", ctypes.c_int)]

# Спільні функції
lib.Free_array.argtypes = [ctypes.POINTER(IntArray)]
lib.Free_array.restype = None
try:
    lib = ctypes.CDLL(lib_path)
except OSError as e:
    print(f"ERROR: Could not load {lib_path}. ")
    raise e

# === Структури даних ===
class IntArray(ctypes.Structure):
    _fields_ = [("data", ctypes.POINTER(ctypes.c_int)), ("size", ctypes.c_int)]

# НОВЕ: Структура для дробових чисел (координати ворогів)
class FloatArray(ctypes.Structure):
    _fields_ = [("data", ctypes.POINTER(ctypes.c_float)), ("size", ctypes.c_int)]

# === Функції очищення пам'яті ===
lib.Free_array.argtypes = [ctypes.POINTER(IntArray)]
lib.Free_array.restype = None

# НОВЕ: Очищення float масиву
lib.Free_float_array.argtypes = [ctypes.POINTER(FloatArray)]
lib.Free_float_array.restype = None