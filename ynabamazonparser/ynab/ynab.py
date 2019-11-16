from ynabamazonparser import utils


def adjust_all_items(transactions, orders_by_transaction_id, items_by_order_id):
    for t in transactions:
        if t.id not in orders_by_transaction_id:
            continue
        order = orders_by_transaction_id[t.id]
        items = items_by_order_id[order.order_id]
        adjust_items(t, order, items)


def adjust_items(t, order, items):
    ''' Ensures that the sum of item prices equals the transaction amount '''
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

def annotate_for_locating(transaction, order):
    transaction.memo = order.order_id

def update(transaction):
    if len(items) > 1:
        annotate_for_locating(transaction, order)
    else:

