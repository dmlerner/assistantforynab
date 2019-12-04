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
        return sum(g.need() for g in self.goals)

    def normalized_rates(self):
        # or 1 handles the days_remaining is None case
        weighted_days = [(g.days_remaining() or 1) * 1 / w for (w, g) in zip(self.weights, self.goals)]
        return [w / sum(weighted_days) for w in weighted_days]

    def total_available(self):
        return sum(g.available() for g in self.goals)

    def withdraw_all(self):
        self.fix_negative_available()  # TODO speed this up, or manage to need it less
        return sum(g.withdraw_all() for g in self.goals)

    def withdraw_surplus(self):
        self.fix_negative_available()
        return sum(g.withdraw_surplus() for g in self.goals)

    def surplus(self):
        return sum(g.surplus() for g in self.goals)

    def delta(self):
        return sum(g.delta for g in self.goals)

    @staticmethod
    def to_integer_cents(vals):
        # vals in milliunits, ie tenths of a cent
        initial_total = sum(vals)

        def sign(x):
            return 1 if x > 0 else -1
        change = 0
        for i, v in enumerate(vals):
            fractional_cents = v - round(v, -1)
            ya.utils.log_debug('frac, v', fractional_cents, v)
            delta = fractional_cents
            change += delta
            vals[i] -= delta
        ya.utils.log_debug('change, vals, current total', change, vals, sum(vals))
        sorted_vals = sorted(vals, key=abs, reverse=True)
        assert all(v % 10 == 0 for v in vals)

        for v in sorted_vals:
            if abs(change) < .1:
                break
            i = vals.index(v)
            delta = max(.01 * abs(v), abs(change))
            vals[i] += delta * sign(change)
            change -= delta * sign(change)
        vals[0] += int(change)
        total = sum(vals)

        ya.utils.log_debug('vals, initial total, total', vals, initial_total, total)
        assert ya.utils.equalish(total, initial_total, 0)
        return list(map(int, vals))

    def distribute(self, amount=0):
        '''
        Make all goals have equal budget rates required
        '''
        ya.utils.log_debug('dist', self, amount)
        ya.utils.log_debug(self, amount)
        # if int(amount) == 0:
        #    return
        ya.utils.log_info(self, self.total_available(), amount)
        assert self.total_available() + amount >= 0
        self.goals[0].adjust_budget(amount)

        need = self.total_need()
        rates = self.normalized_rates()
        adjustments = [g.need() - r * need for r, g in zip(rates, self.goals)]
        for a, g in zip(adjustments, self.goals):
            g.adjust_budget(a, True)

        wg = list(zip(self.weights, self.goals))
        assert all(ya.utils.equalish(w1 * g1.budget_rate_required(), w2 * g2.budget_rate_required())
                   for ((w1, g1), (w2, g2)) in zip(wg, wg[1:]))
        assert ya.utils.equalish(self.total_need(), need, 0)

        integer_adjustments = Priority.to_integer_cents(adjustments)
        for a, ia, g in zip(adjustments, integer_adjustments, self.goals):
            g.adjust_budget(a - ia, True)

        ya.utils.log_debug('total_need(), need', self.total_need(), need)
        assert ya.utils.equalish(self.total_need(), need, 0)
        for g in self.goals:
            g.fix_fractional_cents()

        self.fix_negative_available()

    def fix_negative_available(self):
        ''' Want distribute to never make sum of negative balances worse '''
        need_fixing = [g for g in self.goals if g.available() < 0]
        assert len(need_fixing) != len(self.goals)
        ya.utils.log_info(len(need_fixing), len(self.goals))
        if not need_fixing:
            return
        deficit = sum(g.available() for g in need_fixing)
        need = self.total_need()
        for g in need_fixing:
            self.goals.remove(g)
            g.adjust_budget(-g.available())
        self.distribute(deficit)
        self.goals.extend(need_fixing)
        ya.utils.log_debug('total_need after, before', self.total_need(), need)
        assert ya.utils.equalish(self.total_need(), need, -1)

    def __str__(self):
        table = ya.utils.formatter.Table([g.to_record() for g in self.goals], 'TITLE')
        return str(table)
