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
        while source is not sink:
            need = sink.get_total_need()
            if yap.utils.equalish(need, 0):
                sink = next(important)
            available = source.get_total_available()
            if available <= 0:
                source = next(unimportant)
            use = min(available, need)
            before = source.get_total_available() + sink.get_total_available()
            source.distribute(-use)
            sink.distribute(use)
            after = source.get_total_available() + sink.get_total_available()
            assert yap.utils.equalish(after, before)

    def __repr__(self):
        return '\n'.join(map(str, self.priorities))


class Priority:

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

    def distribute(self, amount=0):
        '''
        Make all goals have equal budget rates required
        Return any excess
        '''
        yap.utils.log_debug(self, amount)
        assert self.get_total_available() + amount >= 0
        self.categories[0].adjust_budget(amount)
        need = self.get_total_need()
        rates = self.get_normalized_rates()
        for r, c in zip(rates, self.categories):
            c.adjust_budget(c.goal_amount_remaining() - r * need)

        assert yap.utils.equalish(self.get_total_need(), need)

        wc = list(zip(self.weights, self.categories))
        assert all(yap.utils.equalish(w1 * c1.budget_rate_required(), w2 * c2.budget_rate_required())
                   for ((w1, c1), (w2, c2)) in zip(wc, wc[1:]))

        self.fix_negative_balance()

    def fix_negative_balance(self):
        ''' Want distribute to never make sum of negative balances worse '''
        need = self.get_total_need()
        need_fixing = [c for c in self.categories if c.balance < 0]  # TODO generalize along with get_total_available
        if not need_fixing:
            return
        deficit = sum(c.balance for c in need_fixing)
        for c in need_fixing:
            self.categories.remove(c)
            c.adjust_budget(-c.balance)
        self.distribute(deficit)
        self.categories.extend(need_fixing)
        assert yap.utils.equalish(self.get_total_need(), need)

    def __repr__(self):
        self.categories.sort(key=lambda c: c.name)
        return '\n'.join(map(str, self.categories))
