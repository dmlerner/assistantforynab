import re
from copy import deepcopy

from ynabamazonparser.ynab.transaction import Transaction
from ynabamazonparser import utils
from ynabamazonparser.config import settings


def annotate(t, order, items):
    t.date = order._order_date
    if len(items) == 1:
        annotate_with_item(t, items[0])
        t.memo += ' ' + order.order_id
    else:
        t.memo = order.order_id
        t.subtransactions = [deepcopy(t) for i in items]
        for i, s in zip(items, t.subtransactions):
            annotate_with_item(s, i)


def annotate_with_item(t, i):
    t.payee_name = i.seller
    t.memo = i.title
    t.amount = i.item_total
    t.category = get_category(i)


def get_category(item):
    return settings.default_category


def get_eligible_transactions(transactions):
    predicates = newer_than, has_blank_or_WIP_memo, matches_account, Transaction.is_outflow
    eligible = [t for t in transactions if all(p(t) for p in predicates)]
    utils.log(
        'Found %s transactions to attempt to match with Amazon orders' % len(eligible))
    if not eligible:
        utils.log('No transactions matching predicates')
        utils.quit()
    return eligible


def has_blank_memo(t):
    return not t.memo


def has_order_number_memo(t):
    return bool(re.match(r'^\d{3}-\d{7}-\d{7}$', t.memo))


def has_blank_or_WIP_memo(t):
    return has_blank_memo(t) or has_order_number_memo(t)


def matches_account(t):
    return t.account_name.lower() == settings.account_name.lower()


def newer_than(t, days_ago=30):
    return utils.newer_than(t.date, days_ago)
