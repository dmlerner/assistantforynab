import collections

import ynabamazonparser as yap


class Budgeter:
    def __init__(self, *p):
        self.priorities = p

    def budget(self):
        ''' Fund high priority categories by withdrawing from low priority categories '''
        important = iter(self.priorities)
        unimportant = reversed(self.priorities)
        sink = next(important)
        source = next(unimportant)
        excess = 0
        while source is not sink:
            if yap.utils.equalish(sink.get_total_need(), 0):
                sink = next(important)
            available = source.get_total_available()
            if yap.utils.equalish(available, 0):
                # TODO: do I need equalish, here, in 28, or elsewhere?
                # fuck floats
                source = next(unimportant)
            # generally this will return zero, unless all source goals entail negative balance
            excess += source.distribute(-available)
            excess = source.distribute(sink.distribute(available + excess))
        return excess

    def __repr__(self):
        return '\n'.join(map(str, self.priorities))


class Priority:
    ''' Allows negative balance, but you really shouldn't do that '''
    def __init__(self, categories, weights=None):
        assert all(isinstance(c, yap.ynab.category.Category) for c in categories)
        # inherently, priority of a goal with days remaining is higher, so it makes no sense to mix them
        assert sum(c.goal_days_remaining() is None for c in categories) in (0, len(categories))

        weights = weights or [1] * len(categories)
        assert all(type(w) in (int, float) for w in weights)
        assert all(w > 0 for w in weights)

        assert len(categories) == len(weights)

        self.categories = categories
        self.weights = list(weights)

    def get_total_need(self):
        return sum(c.goal_amount_remaining() for c in self.categories)

    def get_total_available(self):
        # TODO this is complicated, because credit cards can go negative
        # and other categories can although that's not good behavior
        return sum(c.balance for c in self.categories)

    def get_normalized_rates(self):
        weighted_days = [c.goal_days_remaining() * 1 / w for (w, c) in zip(self.weights, self.categories)]
        return [w / sum(weighted_days) for w in weighted_days]

    def redistribute(self):
        '''
        Make all goals have equal budget rates required
        Return any excess
        '''
        need = self.get_total_need()
        if need > 0:
            rates = self.get_normalized_rates()
            for r, c in zip(rates, self.categories):
                c.adjust_budget(c.goal_amount_remaining() - r * need)
            assert yap.utils.equalish(self.get_total_need(), need)
            # return 0 # this happens implicitly

        else:
            # if need <= 0:
            for c in self.categories:
                c.adjust_budget(c.goal_amount_remaining())
            assert yap.utils.equalish(self.get_total_need(), 0)
            # return -need # happens implicitly

        wc = list(zip(self.weights, self.categories))
        assert all(yap.utils.equalish(w1 * c1.budget_rate_required(), w2 * c2.budget_rate_required())
                   for ((w1, c1), (w2, c2)) in zip(wc, wc[1:]))
        return self.get_total_need() - need

    def distribute(self, amount):
        self.categories[0].adjust_budget(amount)
        return self.redistribute()

    def __repr__(self):
        return '\n'.join(map(str, self.categories))
