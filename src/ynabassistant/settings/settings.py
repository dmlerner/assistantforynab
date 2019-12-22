from . import paths
import json
import shutil


class Settings:
    def __init__(self):
        self.settings = {}

    def load_dict(self, d):
        print('load_dict')
        self.settings = d

    def load_json(self, path=paths.settings_path):
        print('load_json')
        with open(path) as f:
            self.load_dict(json.load(f))

    def clear(self):
        print('clear')
        self.settings = {}

    def __setitem__(self, k, v):
        print('setitem', k, v)
        self.settings[k] = v

    def __getitem__(self, k):
        print('__getitem__')
        #import pdb; pdb.set_trace()
        return self.settings.get(k)

    def save(self, path=paths.settings_path):
        print('save')
        with open(path, 'w') as f:
            json.dump(self.settings, f)


def copy_default_settings():
    print('copying default settings')
    shutil.copy(paths.default_settings_path, paths.settings_path)


_s = Settings()
