from . import utils
print(utils)


class Cache:
    def __init__(self):
        self.xs = []
        self.ids = {}
        self.make_get_by_name()
        self.history = []

    @utils.listy_method
    def store(self, xs):  # TODO listy?
        self.xs = self.filter(xs)
        self.ids = utils.by(self.xs, self.id)
        self.make_get_by_name()
        self.history.append(self.xs)

    def __iter__(self):
        return iter(self.xs)

    def make_get_by_name(self):
        grouped = utils.group_by(self.xs, self.name)
        self.names = utils.by(map(lambda v: v.pop(), grouped.values()), self.name)
        for name, g in grouped.items():
            if g:
                utils.log_debug('duplicate name, using first', name, self.names[name], *g)

    def filter(self, xs):
        return xs

    def id(self, x):
        return x.id

    def get(self, id):
        return self.ids.get(id)

    def name(self, x):
        return x.name

    def by_name(self, name):
        return self.names.get(name)

    def __len__(self):
        return len(self.xs)


class TransactionCache(Cache):
    def __init__(self, account_cache):
        super().__init__()
        self.account_cache = account_cache

    def filter(self, xs):
        # Addresses bug
        return list(filter(lambda x: x.account_id in self.account_cache.ids, xs))

    def name(self, x):
        return x.account_name

    def make_get_by_name(self):
        self.names = utils.group_by(self.xs, self.name)
