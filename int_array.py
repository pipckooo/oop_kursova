import ctypes


class IntArray(ctypes.Structure):
    _fields_ = [("data", ctypes.POINTER(ctypes.c_int)), ("size", ctypes.c_int)]