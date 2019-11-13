import datetime
import os
import sys
import pdb
import time
import re

import settings
import utils
import amazon_downloader
import match
import ynab_gui_client

from ynab_sdk import YNAB
import pdb
import datetime

api = YNAB(settings.api_key)

def get_all_transactions():
    transactions = api.transactions.get_transactions(settings.budget_id).data.transactions
    utils.log('Found %s transactions' % len(transactions) if transactions else 0)
    transactions.sort(key=lambda t:utils.datetime_from_ynab_date(t.date), reverse=True)
    return transactions

def update(transaction):
    return api.transactions.update_transaction(settings.budget_id, transaction)

def update_all(transactions, orders_by_transaction_id):
    for t in transactions:
        if t.id in orders_by_transaction_id:
            update(t)

def get_transactions_to_update():
    all_transactions = get_all_transactions()
    predicates = newer_than, has_blank_or_WIP_memo, matches_account, is_purchase 
    eligible = [t for t in all_transactions if all(p(t) for p in predicates)]
    utils.log('Found %s transactions to attempt to match with Amazon orders' % len(eligible))
    return eligible

def has_blank_memo(t):
    return not t.memo

def has_order_number_memo(t):
    return re.match('^\d{3}-\d{7}-\d{7}$', t.memo)

def has_blank_or_WIP_memo(t):
    return has_blank_memo(t) or has_order_number_memo(t)

def matches_account(t):
    return t.account_name.lower() == settings.account_name.lower()

def is_purchase(t):
    return t.amount < 0

def newer_than(t, days_ago=30):
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days_ago)
    return utils.datetime_from_ynab_date(t.date) > cutoff
