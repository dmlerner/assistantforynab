import datetime
import re

from ynabamazonparser import utils, amazon, match, ynab
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
    return transactions


def update(transaction):
    return api.transactions.update_transaction(settings.budget_id, transaction)


def update_all(transactions, orders_by_transaction_id):
    for t in transactions:
        if t.id in orders_by_transaction_id:
            update(t)


def get_transactions_to_update():
    all_transactions = get_all_transactions()
    predicates = newer_than, has_blank_or_WIP_memo, matches_account, Transaction.is_outflow
    #for i, t in enumerate(all_transactions[:200]):
        #utils.log(i, *[p(t) for p in predicates], t.date, t.amount)
    #closeness = [sum(p(t) for p in predicates) for t in all_transactions]
    #utils.log(closeness)
    eligible = [t for t in all_transactions if all(p(t) for p in predicates)]
    utils.log(
        'Found %s transactions to attempt to match with Amazon orders' % len(eligible))
    if not eligible:
        utils.log('No transactions matching predicates')
        utils.quit()
    return eligible


def has_blank_memo(t):
    return not t.memo


def has_order_number_memo(t):
    return bool(re.match('^\d{3}-\d{7}-\d{7}$', t.memo))


def has_blank_or_WIP_memo(t):
    return has_blank_memo(t) or has_order_number_memo(t)


def matches_account(t):
    return t.account_name.lower() == settings.account_name.lower()


def newer_than(t, days_ago=30):
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days_ago)
    return t.date > cutoff
