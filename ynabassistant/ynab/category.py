import re
import datetime

#from ynab_api.api.models.responses.category import Category as _Category
from ynab_api import Category as _Category

import ynabassistant as ya


class Category:
    def __init__(self, c, category_group_name=None):
        d = c if isinstance(c, dict) else c.__dict__
        self._parent_dict = d.copy()
        self.id = d['id']
        self.name = d['name']
        self.budgeted = d['budgeted']
        self.activity = d['activity']
        self.balance = ya.ynab.utils.parse_money(d['balance'])  # "Available" in web app
        self.goal_type = d['goal_type']
        self.goal_target = ya.ynab.utils.parse_money(d['goal_target'])
        self.goal_target_month = ya.ynab.utils.parse_date(d['goal_target_month'])
        self.category_group_name = category_group_name
        self.category_group_id = d['category_group_id']
        self.is_credit_card_payment = self.category_group_name in ya.settings.credit_card_group_names

    def goal_days_remaining(self):
        if not self.goal_type:
            return None
        if self.goal_type == 'TBD' and not self.goal_target_month:
            return None
        deadline = self.goal_target_month or ya.ynab.utils.first_of_coming_month()
        days_timedelta = deadline - ya.utils.now()
        one_day = datetime.timedelta(1)
        return days_timedelta.total_seconds() / one_day.total_seconds()

    def goal_amount_remaining(self):
        if not self.goal_type:
            return None
        progress = self.balance if self.goal_type == 'TBD' else self.budgeted
        return self.goal_target - progress

    def budget_rate_required(self):
        if not self.goal_type:
            return None
        return self.goal_amount_remaining() / self.goal_days_remaining()

    def __repr__(self):
        money_fields = tuple(map(ya.utils.format_money, (self.goal_amount_remaining(),
                                                         self.balance, self.budgeted, self.budget_rate_required())))
        str_fields = (self.name, self.goal_days_remaining()) + money_fields
        return ' | '.join(map(str, str_fields))

    def adjust_budget(self, amount):
        self.balance += amount
        self.budgeted += amount
