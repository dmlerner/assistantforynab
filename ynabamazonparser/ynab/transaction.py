import re

from ynab_sdk.api.models.responses.transactions import Transaction as _Transaction

import ynabamazonparser as yap


class Transaction:

    def __init__(self, t):
        assert type(t) is _Transaction
        d = t.__dict__
        self._parent_dict = d
        self.amount = yap.ynab.utils.parse_money(t.amount)
        self.date = yap.ynab.utils.parse_date(t.date)
        self.account_name = t.account_name
        self.id = t.id
        self.subtransactions = [Transaction(s) for s in t.subtransactions]

    def is_outflow(self):
        return self.amount < 0

    def is_inflow(self):
        return self.amount > 0

    def to_parent(self):
        d = self.__dict__.copy()
        d['amount'] = int(self._amount)
        d['date'] = self._date
        del d['_amount']
        del d['_date']
        return _Transaction(**d)

    def __repr__(self):
        if not self.subtransactions:
            str_fields = [self._date, '$' + str(round(self.amount, 2)), self.account_name, self.id]
            if self.id not in self.memo:
                str_fields.append(self.memo)
            return ' | '.join(map(str, str_fields)) 
        return '\n'.join(map(str, self.subtransactions))[:-5] 


def starts_with_id(s):
    alphanumeric = '[a-z0-9]'
    return re.match('^x{8}-x{4}-x{4}-x{12}'.replace('x', alphanumeric), s)
