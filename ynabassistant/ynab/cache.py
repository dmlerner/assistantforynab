import ynabassistant as ya


class Cache:
    def __init__(self):
        self.xs = []
        self.xs_by_id = {}
        self.xs_by_name = {}
        self.history = []

    def store(self, xs):  # TODO listy?
        self.xs = self.filter(xs)
        self.xs_by_id = ya.utils.by(self.xs, self.id)
        self.xs_by_name = ya.utils.by(self.xs, self.name)
        self.history.append(self.xs)

    def __iter__(self):
        return iter(self.xs)

    def filter(self, xs):
        return xs

    def id(self, x):
        return x.id

    def get(self, id):
        return self.xs_by_id.get(id)

    def name(self, x):
        return x.name

    def get_name(self, name):
        return self.xs_by_name.get(name)

    def len(self):
        return len(self.xs)


class TransactionCache(Cache):
    def __init__(self, account_cache):
        self.account_cache = account_cache

    def filter(self, xs):
        # Addresses bug
        return filter(lambda x: x.account_id in self.account_cache.xs_by_id)

    def name(self, x):
        return x.account_name
