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
        self.goal_goal_month = yap.ynab.utils.parse_date(d['goal_goal_month'])
        self.category_group_name = d['category_group_name']
        self.category_group_id = d['category_group_id']
        self.is_credit_card_payment = self.category_group_name in yap.settings.credit_card_group_names

    '''
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
    '''

    def goal_amount_remaining(self):
        if self.goal_type in ('NEED', 'MF'):
            progress = self.budgeted
        elif self.goal_type in ('TBD',):
            progress = self.balance
        return self.goal_target - progress

    def goal_amount_remaining(self):
        if not self.is_credit_card_payment:
            if gt == 'NEED':
                progress = self.budgeted

    def goal_time_remaining(self):
        if self.goal_type == 'MF' or self.is_credit_card_payment and self.goal_type == 'NEED':
            deadline = first_of_coming_month
        elif self.goal_type == 'NEED' and self.goal_target_month:
            deadline = self.goal_target_month


        return self.goal_target_month - self.goal_creation_month
'''
    def goal_percentage(self):
        return self.goal_amount_remaining() / self.goal_target

         if not self.is_credit_card_payment:
             if gt == 'NEED':
-                progress = self.budgeted
                 if self.goal_target_month:
                     deadline = self.goal_target_month
                 else:
@@ -110,16 +107,13 @@ class Category(_Category):
                 deadline = first_of_coming_month
             elif gt == 'TBD':
                 if self.goal_target_month:
-                    progress = self.balance
                     deadline = self.goal_target_month
                 else:
                     return None
         else:
             if gt == 'MF':  # budget an amount this month
-                progress = self.budgeted
                 deadline = first_of_coming_month
             elif gt == 'TBD':  # have an amount by some month
-                progress = self.balance
                 deadline = self.goal_target_month
'''


    def goal_budget_rate(self):

        if not self.is_credit_card_payment:
            if gt == 'NEED':
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
                    deadline = self.goal_target_month
                else:
                    return None
        else:
            if gt == 'MF':  # budget an amount this month
                deadline = first_of_coming_month
            elif gt == 'TBD':  # have an amount by some month
                deadline = self.goal_target_month

        remaining_amount = self.goal_target - progress
        one_day = datetime.datetime.timedelta(1)
        remaining_days = (deadline - now).total_seconds() / one_day.total_seconds()
        return remaining_amount / remaining_days
