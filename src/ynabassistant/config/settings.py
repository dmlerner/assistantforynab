import config
import json


class Settings:
    def load_dict(self, d):
        self.__dict__.update(d)

    def load_json(self, path):
        with open(path) as f:
            self.load_dict(json.load(f))

    def reload(self):
        self.__dict__ = {}

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __getitem__(self, k):
        return self.__dict__.get(k)

    def save(self, path):
        with open(path) as f:
            json.dump(self.__dict__, f)


settings = Settings()
settings.load_json(config.settings_path)
