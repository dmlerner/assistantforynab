import ynab_api
from assistantforynab.utils import utils
import ynab
from assistantforynab.assistant import Assistant


class Goal:

    def __init__(self, category):
        assert isinstance(category, ynab_api.Category)
        self.category = category
        self.credit_card = Assistant.accounts.by_name(category.name)
        self.min_balance = 0  # TODO: credit cards
        self.delta = 0

    def days_remaining(self):
        if not self.is_goal():
            return None
        if self.category.goal_type == 'TB' and not self.category.goal_target_month:
            return None
        deadline = self.category.goal_target_month or ynab.first_of_coming_month()
        return utils.day_delta(deadline)

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
        return str(vars(self))

    def to_record(self):
        money_fields = utils.formatter.Field.make_fields({
            'Need': self.need(),
            'Surplus': self.surplus(),
            'Balance': self.category.balance,
            'Budgeted': self.category.budgeted,
            'Delta': self.delta,
            'BRR': self.budget_rate_required()
        }, ynab.format_money)
        string_fields = utils.formatter.Field.make_fields({
            'Name': self.category.name,
            'Days': utils.maybe_round(self.days_remaining(), 1),
        })
        return utils.formatter.Record(string_fields + money_fields)

    def __str__(self):
        return str(self.to_record())

    def adjust_budget(self, amount, allow_noninteger=False):
        utils.log_debug('adjust_budget', amount, self)
        if not allow_noninteger:
            assert isinstance(amount, int)
        self.delta += amount
        self.category.balance += amount
        self.category.budgeted += amount

    def fix_fractional_cents(self):
        assert utils.equalish(self.category.balance, round(self.category.balance, -1), -1)
        assert utils.equalish(self.category.budgeted, round(self.category.budgeted, -1), -1)
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
        return max(0, self.category.balance - self.min_balance)

    def surplus(self):
        return max(0, -self.need())

    def deficit(self):
        return max(0, self.min_balance - self.category.balance)

    def is_static(self):
        return self.is_goal() and (self.days_remaining() is None)

    def is_timed(self):
        return self.is_goal() and (self.days_remaining() is not None)

    def is_goal(self):
        return bool(self.category.goal_type)
