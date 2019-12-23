from .paths import *
from .settings import _s
import assistantforynab.settings.settings
import os

get = _s.__getitem__  # useful only if you want to check if setting is defined and default to None


def set(k, v):
    _s[k] = v
    globals()[k] = v
    _s.save()


def clear():
    for k in _s.settings:
        del globals()[k]
    _s.clear()


def init(use_defaults=False):
    if use_defaults or not os.path.exists(settings_path):
        clear()
        assistantforynab.settings.settings.copy_default_settings()
    _s.load_json()
    globals().update(_s.settings)
