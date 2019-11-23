import datetime
import re

import ynab_api

import ynabassistant as ya


def parse_money(price):
    if price is None:
        return None
    assert isinstance(price, int)
    return price / 1000


def amount(t):
    assert type(t) in (ynab_api.TransactionDetail, ynab_api.SubTransaction)
    return parse_money(t.amount)


def to_milliunits(p):
    return int(p * 1000)


date_format = '%Y-%m-%d'


def parse_date(d):
    if not d:
        return None
    return ya.utils.parse_date(d, date_format)


def format_date(d):
    return ya.utils.format_date(d, date_format)


def first_of_coming_month():
    now = ya.utils.now()
    next_month = now.month + 1
    if next_month == 13:
        next_month = 1
    return datetime.datetime(now.year + (next_month == 1), next_month, 1)


def starts_with_id(s):
    alphanumeric = '[a-z0-9]'
    return re.match('^x{8}-x{4}-x{4}-x{12}'.replace('x', alphanumeric), s)


def calculate_adjustment(t):
    subtransaction_total = sum(s.amount for s in t.subtransactions)
    if ya.utils.equalish(subtransaction_total, t.amount, precision=-1):
        return
    return t.amount - subtransaction_total


def format_transaction(t):
    assert type(t) in (ynab_api.TransactionDetail, ynab_api.SubTransaction)
    t_formatted = ' | '.join(list(map(str, (format_date(t.date), amount(t), t.memo))))
    if isinstance(t, ynab_api.TransactionDetail):
        t_formatted += '\n' + '\n'.join(list(map(format_transaction, t.subtransactions)))
    return t_formatted.strip()
