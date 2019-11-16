from ynabamazonparser import utils
from ynabamazonparser.amazon import downloader
from ynabamazonparser.config import settings

' TODO rename this module '


def get_order(transaction, orders):
    ''' Gets an order corresponding to the ynab transaction '''
    possible_orders = []
    for order in orders:
        order_price = order.total_charged
        transaction_price = transaction.amount
        if utils.equalish(order_price, transaction_price):
            possible_orders.append(order)
    if len(possible_orders) == 0:
        return None
    if len(possible_orders) == 1:
        order = possible_orders[0]
        utils.log('match!', order, transaction)
    else:
        utils.log('ambiguous transaction has %s matches' %
                  len(possible_orders), transaction, possible_orders)
        if settings.fail_on_ambiguous_transaction:
            utils.log('skipping ambiguous transaction')
            return None
        utils.log('choosing the one closest to the order date')
        possible_orders.sort(key=lambda o: time_difference(transaction, o))
        order = possible_orders[0]
    orders.remove(order)
    return order


def time_difference(transaction, order):
    return abs(transaction.date - order.shipment_date)


def get_items(order):
    if not order:
        return None
    return downloader.items_by_order[order.order_id]


def adjust_items(t, order, items):
    ' TODO: improve this; shipping, discounts...'
    item_total = sum(i.item_total for i in items)
    transaction_total = t.amount
    if utils.equalish(transaction_total, item_total):
        return
    adjustment_ratio = transaction_total / item_total
    for i in items:
        i.item_total *= adjustment_ratio
    new_item_total = sum(i.item_total for i in items)
    assert utils.equalish(transaction_total, new_item_total)


def adjust_all_items(transactions, orders_by_transaction_id):
    items_by_order_id = downloader.get_items_by_order_id()
    for t in transactions:
        if t.id not in orders_by_transaction_id:
            continue
        order = orders_by_transaction_id[t.id]
        items = items_by_order_id[order.order_id]
        adjust_items(t, order, items)


def match_all(transactions, orders):
    orders_by_transaction_id = {}
    for i, t in enumerate(transactions):
        order = get_order(t, orders)
        if not order:
            utils.log('No matching order for transaction')
            utils.log(t)
            continue
        t.memo = order.order_id
        orders_by_transaction_id[t.id] = order
    utils.log(downloader.data)
    adjust_all_items(transactions, orders_by_transaction_id)
    return orders_by_transaction_id


'''
Mostly, the amounts map over and are unique
first assume they do
break uniques by date proximity
    do the dates on one of ynab/amazon
    tend to be before/after the other consistently?
napsack the rest
    optimizing for most dollars matched?
'''
'''
y = collections.Counter(ynab.amounts)
a = collections.Counter(amazon.amounts)
ya = y - a
ay = a - y
utils.log(ya)
utils.log(ay)
'''
