import numpy as np
import ctypes as ct
import os

libgamma = ct.CDLL(os.path.dirname(__file__)+"/__data/libgamma/libgamma.so")

_CGammaSpouge = libgamma.GammaSpouge
_CGammaSpouge.argtypes = [ct.c_double]
_CGammaSpouge.restype = ct.c_double

