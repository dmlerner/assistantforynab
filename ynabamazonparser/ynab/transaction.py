import re

from ynab_sdk.api.models.responses.transactions import Transaction as _Transaction

import ynabamazonparser as yap

# transaction_id, amount, memo, payee_id, category_od, transfer_account_id, deleted
class Transaction:

    def __init__(self, t, **kwargs):
        assert type(t) is _Transaction
        d = t.__dict__
        self._parent_dict = d
        self.amount = yap.ynab.utils.parse_money(t.amount)
        self.date = yap.ynab.utils.parse_date(t.date)
        self.account_name = t.account_name
        self.payee_name = t.payee_name
        self.category_name = t.category_name
        self.memo = t.memo
        self.id = t.id
        self.account_id = t.account_id

        # May assume that a _Transaction has no subtransactions, because the api won't return them anyway
        assert not t.subtransactions
        self.subtransactions = [] # [ynab.Transaction]

    def is_outflow(self):
        return self.amount < 0

    def is_inflow(self):
        return self.amount > 0

    def to_parent(self):
        d = self.__dict__.copy()
        d['amount'] = yap.ynab.utils.to_milliunits(self.amount)
        d['date'] = yap.ynab.utils.format_date(self.date)
        yap.utils.filter_dict(d, self._parent_dict)
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
