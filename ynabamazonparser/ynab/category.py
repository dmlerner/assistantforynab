import re
import datetime

from ynab_sdk.api.models.responses.category import Category as _Category
'''
 "data": {
    "category_groups": [
      {
        "id": "string",
        "name": "string",
        "hidden": true,
        "deleted": true,
        "categories": [
          {
            "id": "string",
            "category_group_id": "string",
            "name": "string",
            "hidden": true,
            "original_category_group_id": "string",
            "note": "string",
            "budgeted": 0,
            "activity": 0,
            "balance": 0,
            "goal_type": "TB",
            "goal_creation_month": "string",
            "goal_target": 0,
            "goal_target_month": "string",
            "goal_percentage_complete": 0,
            "deleted": true
          }
        ]
      }
    ],
    "server_knowledge": 0
  }
}
'''


class Category(_Category):
    def __init__(self, c):
        d = c if type(c) is dict else c.__dict__
        self._parent_dict = d.copy()
        self.id = d['id']
        self.name = d['name']
        self.budgeted = d['budgeted']
        self.activity = d['activity']
        self.balance = yap.utils.parse_money(d['balance'])
        self.goal_type = d['goal_type']
        self.goal_target = yap.utils.parse_money(d['goal_target'])
        self.goal_target_month = yap.ynab.utils.parse_date(d['goal_target_month'])
        self.category_group_name = d['category_group_name']
        self.category_group_id = d['category_group_id']
        self.is_credit_card_payment = self.category_group_name in yap.settings.credit_card_group_names

    def to_parent(self):
        d = self.__dict__.copy()
        d['balance'] = int(self._balance)
        d['date'] = self._date
        del d['_balance']
        del d['_date']
        return _Transaction(**d)

    def __repr__(self):
        if not self.subtransactions:
            str_fields = [self._date, '$' + str(round(self.balance, 2)), self.account_name, self.id]
            if self.id not in self.memo:
                str_fields.append(self.memo)
            return ' | '.join(map(str, str_fields))
        return '\n'.join(map(str, self.subtransactions))[:-5]

    def goal_budget_rate(self):
        assert self.goal_type in ('MF', 'TBD', 'NEED', None)
        '''
        8 types
        payment
            None
            MF "pay specific amount monthly" no specific end date chase amazon 2
            TBD "pay off balance by date" amount adjusts if you pay more/less than you should chase amazon
        saving
            None
            NEED w/o goal_target_month "monthly" shaina spending monthly
            NEED w/ goal_target_month "by date" mark/rae spending by date
            MF ('monthly') savings monthly contribution
            TBD ('target budgeted by date') can spend from it xiaolu savings target balance
                may or may not have a date
                if not, no way to have a target rate
        '''
        gt = self.goal_type
        if not gt:
            return None

        now = datetime.datetime.now()
        next_month = now.month + 1
        if next_month == 13:
            next_month = 1
        first_of_coming_month = datetime.datetime(year + next_month == 1, next_month, 1)

        if not self.is_credit_card_payment:
            if gt == 'NEED':
                progress = self.budgeted
                if self.goal_target_month:
                    deadline = self.goal_target_month
                else:
                    deadline = first_of_coming_month
            elif gt == 'MF':
                # only difference from NEED w/o target date is budgeted here resets monthly
                # which doesns't affect my logic
                # just separating the case to match the webapp
                deadline = first_of_coming_month
            elif gt == 'TBD':
                if self.goal_target_month:
                    progress = self.balance
                    deadline = self.goal_target_month
                else:
                    return None
        else:
            if gt == 'MF':  # budget an amount this month
                progress = self.budgeted
                deadline = first_of_coming_month
            elif gt == 'TBD':  # have an amount by some month
                progress = self.balance
                deadline = self.goal_target_month

        remaining_amount = self.goal_target - progress
        one_day = datetime.datetime.timedelta(1)
        remaining_days = (deadline - now).total_seconds() / one_day.total_seconds()
        return remaining_amount / remaining_days
