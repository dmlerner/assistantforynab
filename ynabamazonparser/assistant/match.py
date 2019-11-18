import ynabamazonparser as yap

' TODO rename this module '


def get_order(transaction, orders):
    ''' Gets an order corresponding to the ynab transaction '''
    yap.utils.log_debug('get_order', transaction, orders)
    possible_orders = []
    for order in orders.values():
        if yap.utils.equalish(order.total_charged, transaction.amount):
            possible_orders.append(order)
    if len(possible_orders) == 0:
        yap.utils.log_debug('No matching order for transaction')
        return None
    if len(possible_orders) == 1:
        order = possible_orders[0]
    else:
        if yap.settings.fail_on_ambiguous_transaction:
            yap.utils.log_error('Skipping ambiguous transaction', transaction, possible_orders)
            return None
        else:
            yap.utils.log_debug('Skipping ambiguous transaction', transaction, possible_orders)
        unused_orders = [o for o in possible_orders if o.order_id not in assigned_order_ids]
        unused_orders.sort(key=lambda o: time_difference(transaction, o))
        order = unused_orders[0]
    assigned_order_ids.add(order.order_id)
    yap.utils.log_info('Matched transaction with order', transaction, order)
    return order


# Used to avoid reusing an order for multiple transactions
assigned_order_ids = set()


def time_difference(transaction, order):
    return abs(transaction.date - order.order_date)  # TODO want shipment_date change parser property


def match_all(transactions, orders):
    yap.utils.log_debug('match_all', len(transactions), len(orders))
    orders_by_transaction_id = {}
    for t_id, t in transactions.items():
        order = get_order(t, orders)
        if not order:
            continue
        orders_by_transaction_id[t_id] = order
    return orders_by_transaction_id
