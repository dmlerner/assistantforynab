from ynabamazonparser import utils
from ynab.transaction import Transaction
from ynabamazonparser.config import settings

from ynab_sdk import YNAB

api = YNAB(settings.api_key)


def get_all_transactions():
    transactions = list(map(Transaction, api.transactions.get_transactions(
        settings.budget_id).data.transactions))
    utils.log('Found %s transactions' %
              len(transactions) if transactions else 0)
    transactions.sort(
        key=lambda t: t.date, reverse=True)
    return utils.by(transactions, lambda t: t.id)


def update_all(transactions):
    for t in transactions:
        update(t)


def update(t):
    api.transactions.update_transaction(settings.budget_id, t.to_parent())
