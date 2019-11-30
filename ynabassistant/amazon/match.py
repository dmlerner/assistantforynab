import ynabassistant as ya


def get_order(t, orders):
    ''' Gets an order corresponding to the ynab transaction '''
    ya.utils.log_debug('get_order', t, orders)
    possible_orders = []
    for order in orders.values():
        # need negative because YNAB outflows have negative amount
        if ya.utils.equalish(order.total_charged, -ya.ynab.utils.amount(t)):
            possible_orders.append(order)
    if len(possible_orders) == 0:
        ya.utils.log_debug('No matching order for transaction')
        return None
    if len(possible_orders) == 1:
        order = possible_orders[0]
    else:
        if ya.settings.fail_on_ambiguous_transaction:
            ya.utils.log_error('Skipping ambiguous transaction', t, possible_orders)
            return None
        else:
            ya.utils.log_debug('Skipping ambiguous transaction', t, possible_orders)
        unused_orders = [o for o in possible_orders if o.id not in assigned_ids]
        # TODO want shipment_date change parser property
        unused_orders.sort(key=lambda o: ya.utils.day_delta(t.date, o.order_date))
        order = unused_orders[0]
    assigned_ids.add(order.id)
    ya.utils.log_info('Matched transaction with order', t, order)
    return order


# Used to avoid reusing an order for multiple transactions
assigned_ids = set()


def match_all(transactions, orders):
    ya.utils.log_debug('match_all', len(transactions), len(orders))
    orders_by_transaction_id = {}
    for t_id, t in transactions.items():
        order = get_order(t, orders)
        if not order:
            continue
        orders_by_transaction_id[t_id] = order
    ya.utils.log_info('Found %s matches' % len(orders_by_transaction_id))
    return orders_by_transaction_id
