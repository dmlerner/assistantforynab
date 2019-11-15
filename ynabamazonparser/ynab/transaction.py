from ynab_sdk.api.models.responses.transactions import Transaction as _Transaction
import datetime
from dataclasses import dataclass


@dataclass
class Transaction(_Transaction):
    date_format = '%Y-%m-%d'

    def __init__(self, t):
        self._date = t.date
        self._amount = t.amount
        super().__init__(**t.__dict__)

    @property
    def amount(self):
        return self._amount

    @property
    def date(self):
        return self._date

    # These allow us to not think about milliunits
    @amount.getter
    def amount(self):
        return abs(self._amount/1000)

    @amount.setter
    def amount(self, a):
        self._amount = abs(a*1000) * (1 if self._amount > 0 else -1)

    def is_outflow(self):
        return self._amount < 0

    def is_inflow(self):
        return self._amount > 0

    @date.getter
    def date(self):
        return datetime.datetime.strptime(self._date, Transaction.date_format)

    @date.setter
    def date(self, d):
        if type(d) is datetime.datetime:
            self._date = datetime.strftime(d, Transaction.date_format)
        else:
            # make sure it's a valid format
            datetime.datetime.strptime(d, Transaction.date_format)
            self._date = d
