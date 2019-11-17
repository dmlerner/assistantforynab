from copy import deepcopy

import ynabamazonparser as yap


def annotate(t, order, items):
    t.date = order.order_date
    if len(items) == 1:
        annotate_with_item(t, items[0])
        t.memo += ' ' + order.order_id
    else:
        t.memo = order.order_id
        t.subtransactions = [deepcopy(t) for i in items]
        for i, s in zip(items, t.subtransactions):
            annotate_with_item(s, i)
        assert len(t.subtransactions) == len(items)


def annotate_with_item(t, i):
    t.payee_name = i.seller
    t.memo = i.title
    t.amount = i.item_total
    t.category_name = get_category(i)


def get_category(item):
    return yap.settings.default_category


def get_eligible_transactions(transactions):
    predicates = newer_than, has_blank_or_WIP_memo, matches_account, yap.ynab.transaction.Transaction.is_outflow
    eligible = yap.utils.by(
        filter(
            lambda t: all(p(t) for p in predicates),
            transactions.values()),
        lambda t: t.id)
    yap.utils.log(
        'Found %s transactions to attempt to match with Amazon orders' % len(eligible))
    if not eligible:
        yap.utils.log('No transactions matching predicates')
        yap.utils.quit()
    return eligible


def has_blank_memo(t):
    return not t.memo


def has_blank_or_WIP_memo(t):
    return has_blank_memo(t) or yap.ynab.transaction.starts_with_id(t.memo)


def matches_account(t):
    return t.account_name.lower() == yap.settings.account_name.lower()


def newer_than(t, days_ago=30):
    return yap.utils.newer_than(t.date, days_ago)
