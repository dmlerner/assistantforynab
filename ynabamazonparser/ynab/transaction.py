import re

from ynab_sdk.api.models.requests.transaction import TransactionRequest

import ynabamazonparser as yap

class Transaction:

    def __init__(self, t):
        d = t if type(t) is dict else t.__dict__
        self._parent_dict = d.copy()
        self.amount = yap.ynab.utils.parse_money(d['amount'])
        self.date = yap.ynab.utils.parse_date(d['date'])
        self.account_name = d['account_name']

        self.payee_name = d.get('payee_name')
        if not self.payee_name: # needed for subtransactions; TODO see that ynab converts this
            self.payee_id = d['payee_id']

        self.category_name = d.get('category_name')
        if not self.category_name: # needed for subtransactions
            self.category_id = d['category_id']

        self.memo = d['memo']
        self.id = d['id']

        self.subtransactions = [] # [ynab.Transaction]
        if d.get('subtransactions'):
            for s in d['subtransactions']:
                d = s.__dict__.copy()
                d['date'] = yap.ynab.utils.format_date(self.date)
                d['id'] = self.id
                d['account_name'] = self.account_name
                self.subtransactions.append(Transaction(d))

    def is_outflow(self):
        return self.amount < 0

    def is_inflow(self):
        return self.amount > 0

    def to_transaction_request(self):
        d = self.__dict__.copy()
        d['amount'] = yap.ynab.utils.to_milliunits(self.amount)
        d['date'] = yap.ynab.utils.format_date(self.date)
        d = yap.utils.filter_dict(d, TransactionRequest.__dataclass_fields__)
        return TransactionRequest(**d)

    def __repr__(self):
        if not self.subtransactions:
            str_fields = yap.utils.format_date(self.date), yap.utils.format_money(self.amount), self.account_name, self.memo, self.id
            return ' | '.join(map(str, str_fields))
        return '\n'.join(map(str, self.subtransactions))


def starts_with_id(s):
    alphanumeric = '[a-z0-9]'
    return re.match('^x{8}-x{4}-x{4}-x{12}'.replace('x', alphanumeric), s)
