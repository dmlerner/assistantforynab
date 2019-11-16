from ynabamazonparser import utils
from ynabamazonparser.config import settings

' TODO rename this module '


def get_order(transaction, orders):
    ''' Gets an order corresponding to the ynab transaction '''
    possible_orders = []
    for order in orders.values():
        if utils.equalish(order.total_charged, transaction.amount):
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
        unused_orders = [o for o in possible_orders if o.order_id not in assigned_order_ids]
        unused_orders.sort(key=lambda o: time_difference(transaction, o))
        order = unused_orders[0]
    assigned_order_ids.add(order.order_id)
    return order


# Used to avoid reusing an order for multiple transactions
assigned_order_ids = set()


def time_difference(transaction, order):
    return abs(transaction.date - order.shipment_date)


def match_all(transactions, orders):
    orders_by_transaction_id = {}
    for t_id, t in transactions.items():
        order = get_order(t, orders)
        if not order:
            utils.log('No matching order for transaction')
            utils.log(t)
            continue
        orders_by_transaction_id[t_id] = order
    return orders_by_transaction_id

# TODO: consider having a separation of concerns between matching and modifying transactions
# as a separate step between them in driver
