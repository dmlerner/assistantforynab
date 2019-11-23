import ynabassistant as ya


def load_amazon_data():
    ya.utils.log_info('Loading Amazon')
    global orders, items
    orders = ya.utils.by(ya.amazon.downloader.load('orders'), lambda o: o.order_id)
    items = ya.amazon.downloader.load('items')
    ya.utils.log_info(ya.utils.separator)


def load_ynab_data():
    ya.utils.log_info('Downloading YNAB')
    global transactions, category_groups, categories, payees
    transactions = ya.utils.by(ya.ynab.api_client.get_all_transactions(), lambda t: t.id)
    category_groups = ya.utils.by(ya.ynab.api_client.get_category_groups(), lambda g: g.id)
    categories = ya.utils.by((c for g in category_groups.values() for c in g.categories), lambda c: c.id)
    payees = ya.utils.by(ya.ynab.api_client.get_payees(), lambda p: p.id)
    ya.utils.log_info(ya.utils.separator)


def update_amazon_transactions():
    ya.utils.log_info('Matching Amazon orders to YNAB transactions')
    potential_amazon_transactions = ya.amazon.get_eligible_transactions(transactions)
    orders_by_transaction_id = ya.amazon.match.match_all(potential_amazon_transactions, orders)
    for t_id, order in orders_by_transaction_id.values():
        order = orders_by_transaction_id[t_id]
        i = items[order.order_id]
        assert i
        t = transactions[t_id]
        ya.amazon.annotate(t, order, i)
        ya.ynab.queue_update(t)
    ya.utils.log_info(ya.utils.separator)


def update_ynab():
    ya.ynab.do_rest()
