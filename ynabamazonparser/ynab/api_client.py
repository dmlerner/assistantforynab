from ynab_sdk import YNAB
from ynab_sdk.api.models.requests.transaction import TransactionRequest

import ynabamazonparser as yap

api = YNAB(yap.settings.api_key)


def get_all_transactions():
    raw = api.transactions.get_transactions(yap.settings.budget_id).data.transactions
    transactions = list(map(yap.ynab.transaction.Transaction, raw))
    yap.utils.log('Found %s transactions' %
                  len(transactions) if transactions else 0)
    transactions.sort(
        key=lambda t: t.date, reverse=True)
    yap.utils.log('about to gruop trans', transactions[:10])
    return yap.utils.by(transactions, lambda t: t.id)


def update_all(transactions):
    for t in transactions:
        update(t)


def update(t):
    yap.utils.log('update', t)
    s = t.subtransactions
    t.subtransactions = []
    p = t.to_parent()
    yap.utils.log('parented', p)
    response = api.transactions.update_transaction(yap.settings.budget_id, p)
    if 'error' in response:
        yap.utils.log('ERROR:', response)
    t.subtransactions = s


def create(transactions):
    yap.utils.log('create', transactions)
    transaction_requests = []
    not_using = set()
    for t in transactions:
        p = t.to_parent().__dict__
        yap.utils.log('parented', p)
        for k in p:
            if k not in TransactionRequest.__dataclass_fields__.keys():
                not_using.add(k)
        for k in not_using:
            if k in p:
                del p[k]
        yap.utils.log('clena transactoin: ', p)
        tr = TransactionRequest(**p)
        yap.utils.log('TR', tr)
        transaction_requests.append(tr)
    response = api.transactions.create_transactions(yap.settings.budget_id, transaction_requests)
    yap.utils.log('response', response)
    if 'error' in response:
        yap.utils.log('ERROR:', response)
    yap.utils.log('not using', not_using)
