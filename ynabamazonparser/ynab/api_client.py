from ynab_sdk import YNAB

import ynabamazonparser as yap

api = YNAB(yap.settings.api_key)


def get_all_transactions():
    yap.utils.log_debug('get_all_transactions')
    raw = api.transactions.get_transactions(yap.settings.budget_id).data.transactions
    transactions = list(map(yap.ynab.transaction.Transaction, raw))
    yap.utils.log_info('Found %s transactions' % len(transactions or []))
    transactions.sort(key=lambda t: t.date, reverse=True)
    return yap.utils.by(transactions, lambda t: t.id)


def update_all(transactions):
    yap.utils.log_debug('update_all')
    for t in transactions:
        update(t)


def update(t):
    yap.utils.log_debug('update', t)
    s = t.subtransactions
    t.subtransactions = []
    p = t.to_parent()
    response = api.transactions.update_transaction(yap.settings.budget_id, p)
    if 'error' in response:
        yap.utils.log_error('ERROR:', response)
    t.subtransactions = s


def create(transactions):
    yap.utils.log_debug('create', *transactions)
    transaction_requests = [t.to_transaction_request() for t in transactions]
    response = api.transactions.create_transactions(yap.settings.budget_id, transaction_requests)
    yap.utils.log_debug('response', response)
    if 'error' in response:
        yap.utils.log_error('ERROR:', response)

def get_categories():
    raw_groups = api.categories.get_categories(yap.settings.budget_id).data.category_groups
    raw_categories = (c for g in raw_groups for c in g.categories)
    categories = map(yap.ynab.category.Category, raw_categories)
    return yap.utils.by(categories, lambda c: c.category_group_id)
