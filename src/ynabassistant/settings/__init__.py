from .paths import *
from .settings import _s

get = _s.__getitem__  # useful only if you want to check if setting is defined and default to None


def set(k, v):
    _s[k] = v
    globals()[k] = v
    _s.save()


def load():
    globals().update(vars(_s))
    print(globals().keys())


load()
