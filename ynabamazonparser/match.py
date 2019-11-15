from ynabamazonparser import settings, utils, amazon

' TODO rename this module '


def get_order(transaction, orders):
    ''' Gets an order corresponding to the ynab transaction '''
    possible_orders = []
    for order in orders:
        order_price = utils.float_from_amazon_price(order['Total Charged'])
        transaction_price = utils.float_from_ynab_price(transaction.amount)
        if utils.equalish(order_price, transaction_price):
            possible_orders.append(order)
    if len(possible_orders) == 0:
        return None
    if len(possible_orders) == 1:
        order = possible_orders[0]
    else:
        utils.log('ambiguous transaction has %s matches' %
                  len(possible_orders), transaction, possible_orders)
        if settings.fail_on_ambiguous_transaction:
            utils.log('skipping ambiguous transaction')
            return None
        utils.log('choosing the one closest to the shipping date')
        possible_orders.sort(key=lambda o: time_difference(transaction, o))
        order = possible_orders[0]
    orders.remove(order)
    return order


def time_difference(transaction, order):
    t_transaction = utils.datetime_from_ynab_date(transaction.date)
    t_order = utils.datetime_from_amazon_date(order['Shipment Date'])
    return abs(t_transaction - t_order)


def get_items(order):
    if not order:
        return None
    return amazon.items_by_order[order['Order ID']]


def adjust_items(t, order, items):
    ' TODO: improve this; shipping, discounts...'
    item_total = sum(utils.float_from_amazon_price(
        i['Item Total']) for i in items)
    transaction_total = utils.float_from_ynab_price(t.amount)
    if utils.equalish(transaction_total,  item_total):
        return
    adjustment_ratio = transaction_total / item_total
    for i in items:
        ' TODO clearly we need my own item/order/transaction objects'
        i['Item Total'] = '$' + \
            str(utils.float_from_amazon_price(
                i['Item Total']) * adjustment_ratio)
    new_item_total = sum(utils.float_from_amazon_price(
        i['Item Total']) for i in items)
    assert utils.equalish(transaction_total, new_item_total)


def adjust_all_items(transactions, orders_by_transaction_id):
    items_by_order_id = amazon.downloader.get_items_by_order_id()
    for t in transactions:
        if t.id not in orders_by_transaction_id:
            continue
        order = orders_by_transaction_id[t.id]
        items = items_by_order_id[order['Order ID']]
        adjust_items(t, order, items)


def match_all(transactions, orders):
    orders_by_transaction_id = {}
    for i, t in enumerate(transactions):
        order = get_order(t, orders)
        if not order:
            # utils.log('No order found for transaction\n', t)
            continue
        t.memo = order['Order ID']
        orders_by_transaction_id[t.id] = order
    adjust_all_items(transactions, orders_by_transaction_id)
    return orders_by_transaction_id


'''
Mostly, the amounts map over and are unique
first assume they do
break uniques by date proximity
    do the dates on one of ynab/amazon tend to be before/after the other consistently?
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
