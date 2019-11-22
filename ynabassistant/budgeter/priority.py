import collections

import ynabassistant as ya


class Priority:

    def __init__(self, goals, weights=None):
        assert all(isinstance(g, ya.budgeter.Goal) for g in goals)
        # inherently, priority of a goal with days remaining is higher, so it makes no sense to mix them
        assert sum(g.days_remaining() is None for g in goals) in (0, len(goals))

        weights = weights or [1] * len(goals)
        assert all(type(w) in (int, float) for w in weights)
        assert all(w > 0 for w in weights)

        assert len(goals) == len(weights)

        self.goals = sorted(goals, key=lambda g: g.category.name)
        self.weights = list(weights)

    def total_need(self):
        return sum(g.amount_remaining() for g in self.goals)

    def normalized_rates(self):
        weighted_days = [g.days_remaining() * 1 / w for (w, g) in zip(self.weights, self.goals)]
        return [w / sum(weighted_days) for w in weighted_days]

    def total_available(self):
        return sum(g.available() for g in self.goals)

    def distribute(self, amount=0):
        '''
        Make all goals have equal budget rates required
        '''
        ya.utils.log_debug(self, amount)
        assert self.total_available() + amount >= 0
        self.goals[0].adjust_budget(amount)
        need = self.total_need()
        rates = self.normalized_rates()
        for r, g in zip(rates, self.goals):
            g.adjust_budget(g.amount_remaining() - r * need)

        assert ya.utils.equalish(self.total_need(), need)

        wg = list(zip(self.weights, self.goals))
        assert all(ya.utils.equalish(w1 * g1.budget_rate_required(), w2 * g2.budget_rate_required())
                   for ((w1, g1), (w2, g2)) in zip(wg, wg[1:]))

        self.fix_negative_available()

    def fix_negative_available(self):
        ''' Want distribute to never make sum of negative balances worse '''
        need_fixing = [g for g in self.goals if g.available() < 0]
        if not need_fixing:
            return
        deficit = sum(g.available() for g in need_fixing)
        need = self.total_need()
        for g in need_fixing:
            self.goals.remove(g)
            g.adjust_budget(-g.available())
        self.distribute(deficit)
        self.goals.extend(need_fixing)
        assert ya.utils.equalish(self.total_need(), need)

    def __repr__(self):
        return '\n'.join(map(str, self.goals))
