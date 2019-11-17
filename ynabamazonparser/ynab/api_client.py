from ynab_sdk import YNAB

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
