import ynab_api

import ynabassistant as ya


class Goal:
    def __init__(self, category):
        assert isinstance(category, ynab_api.Category)
        self.category = category
        self.is_credit_card_payment = category.name in ya.settings.credit_card_group_names
        self.delta = 0

    def days_remaining(self):
        if not self.category.goal_type:
            return None
        if self.category.goal_type == 'TB' and not self.category.goal_target_month:
            return None
        deadline = self.category.goal_target_month or ya.ynab.utils.first_of_coming_month()
        return ya.utils.day_delta(deadline)

    def amount_remaining(self):
        if not self.category.goal_type:
            return 0
        progress = self.category.balance if self.category.goal_type == 'TBD' else self.category.budgeted
        return self.category.goal_target - progress

    def budget_rate_required(self):
        days = self.days_remaining() or 1  # works out well/proportionally for static goals
        return self.amount_remaining() / days

    def __repr__(self):
        money_fields = tuple(map(ya.ynab.utils.parse_money,
                                 (self.amount_remaining(),
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

    def available(self):
        return self.category.balance  # TODO

    def is_static(self):
        return bool(self.category.goal_type and (self.days_remaining() is None))

    def is_timed(self):
        return bool(self.category.goal_type and (self.days_remaining() is not None))

    def is_goal(self):
        return bool(self.category.goal_type)
