from . import paths
import json
import shutil
import os
import sys


class Settings:

    def load_dict(self, d):
        self.__dict__.update(d)

    def load_json(self, path=paths.settings_path):
        with open(path) as f:
            self.load_dict(json.load(f))

    def reload(self):
        self.__dict__ = {}

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __getitem__(self, k):
        return self.__dict__.get(k)

    def save(self, path=paths.settings_path):
        with open(path, 'w') as f:
            json.dump(self.__dict__, f)


def copy_default_settings(clean=False):
    if clean or not os.path.exists(paths.settings_path):
        shutil.copy(paths.default_settings_path, paths.settings_path)

#copy_default_settings(True)
copy_default_settings()
_s = Settings()
_s.load_json()
