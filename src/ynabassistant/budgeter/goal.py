import ynab_api

import ynabassistant as ya


class Goal:

    def __init__(self, category):
        assert isinstance(category, ynab_api.Category)
        self.category = category
        self.credit_card = ya.Assistant.accounts.by_name(category.name)
        self.delta = 0

    def days_remaining(self):
        if not self.is_goal():
            return None
        if self.category.goal_type == 'TB' and not self.category.goal_target_month:
            return None
        deadline = self.category.goal_target_month or ya.ynab.utils.first_of_coming_month()
        return ya.utils.day_delta(deadline)

    def need(self):  # TODO: custom credit card goal types: net budgeted per month, always pay off
        if not self.is_goal():
            return min(0, -self.available())
        if self.category.goal_type == 'TBD':  # Target By Date
            progress = self.category.balance
            if self.credit_card:
                progress += self.credit_card.balance  # negative in general
        else:  # TB = Target Budgeted
            progress = self.category.budgeted
            # if self.credit_card: # This seems reasonable, but isn't how the official goal type works
            #     progress += self.category.activity

        need = self.category.goal_target - progress
        return need

    def budget_rate_required(self):
        days = self.days_remaining() or 1  # works out well/proportionally for static goals
        return self.need() / days

    def __repr__(self):
        money_fields = tuple(map(ya.ynab.utils.parse_money,
                                 (self.need(),
                                  self.category.balance,
                                  self.category.budgeted,
                                  self.delta,
                                  ya.utils.maybe_round(self.budget_rate_required()))))
        str_fields = (self.category.name, ya.utils.maybe_round(self.days_remaining(), 1)) + money_fields
        return ' | '.join(map(str, str_fields))

    def adjust_budget(self, amount, allow_noninteger=False):
        ya.utils.log_debug('adjust_budget', amount, self)
        if not allow_noninteger:
            assert isinstance(amount, int)
        self.delta += amount
        self.category.balance += amount
        self.category.budgeted += amount

    def fix_fractional_cents(self):
        ya.utils.log_debug(self, self.category)
        ya.utils.log_debug(self.category.balance, round(self.category.balance))
        ya.utils.log_debug(self.category.budgeted, round(self.category.budgeted))
        assert ya.utils.equalish(self.category.balance, round(self.category.balance, -1), -1)
        assert ya.utils.equalish(self.category.budgeted, round(self.category.budgeted, -1), -1)
        self.category.budgeted = int(self.category.budgeted)
        self.category.balance = int(self.category.balance)

    def withdraw_all(self):
        available = self.available()
        self.adjust_budget(-available)
        return available

    def withdraw_surplus(self):
        surplus = self.surplus()
        self.adjust_budget(-surplus)
        return surplus

    def available(self):
        return max(0, self.category.balance)  # TODO

    def surplus(self):
        return max(0, -self.need())

    def is_static(self):
        return self.is_goal() and (self.days_remaining() is None)

    def is_timed(self):
        return self.is_goal() and (self.days_remaining() is not None)

    def is_goal(self):
        return bool(self.category.goal_type)
