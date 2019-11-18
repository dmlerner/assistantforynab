import re
import datetime
from dataclasses import dataclass

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


@dataclass
class Category(_Category):
    def __init__(self, c):
        d = c.__dict__
        self._balance = d['balance']  # hacky
        d['balance'] /= 1000
        super().__init__(**d)
        self._date = t.date

    @property
    def balance(self):
        return self._balance

    @property
    def date(self):
        return self._date

    # These allow us to not think about milliunits
    @balance.getter
    def balance(self):
        return abs(self._balance / 1000)

    @balance.setter
    def balance(self, a):
        self._balance = abs(1000 * a) * (1 if self._balance > 0 else -1)

    @date.getter
    def date(self):
        return datetime.datetime.strptime(self._date, yap.ynab.ynab.date_format)

    @date.setter
    def date(self, d):
        if isinstance(d, datetime.datetime):
            self._date = datetime.datetime.strftime(d, yap.ynab.ynab.date_format)
        else:
            # make sure it's a valid format
            datetime.datetime.strptime(d, yap.ynab.ynab.date_format)
            self._date = d

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
        assert self.goal_type in 'MF', 'TBD', 'NEED', None
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

        if savings:
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
        elif:  # payment
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
