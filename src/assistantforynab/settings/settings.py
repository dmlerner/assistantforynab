from . import paths
import json
import shutil


class Settings:
    def __init__(self):
        self.settings = {}

    def load_dict(self, d):
        self.settings = d

    def load_json(self, path=paths.settings_path):
        with open(path) as f:
            self.load_dict(json.load(f))

    def clear(self):
        self.settings = {}

    def __setitem__(self, k, v):
        self.settings[k] = v

    def __getitem__(self, k):
        return self.settings.get(k)

    def save(self, path=paths.settings_path):
        with open(path, 'w') as f:
            json.dump(self.settings, f)


def copy_default_settings():
    shutil.copy(paths.default_settings_path, paths.settings_path)


_s = Settings()
