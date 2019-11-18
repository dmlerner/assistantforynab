from copy import deepcopy

import ynabamazonparser as yap

# Needed iff changing subtransactions
# I'm abusing subtransactions field by storing [ynab.Transactions]
# Instead of [official api subtransaction]
transactions_to_gui_update = []

# Any changes to subtransactions are ignored
transactions_to_rest_update = []


def add_adjustment_subtransaction(t):
    ''' Ensures that the sum of subtransaction prices equals the transaction amount '''
    yap.utils.log_debug('add_adjustment_subtransaction')
    subtransaction_total = sum(s.amount for s in t.subtransactions)
    if yap.utils.equalish(subtransaction_total, t.amount):
        return
    adjustment = deepcopy(t)
    adjustment.subtransactions = []
    adjustment.memo = 'Split transaction adjustment'
    adjustment.amount = t.amount - subtransaction_total
    adjustment.category_name = yap.settings.default_category  # TODO
    yap.utils.log_info('Warning, adjusting: subtransactions do not add up, by $%s' % adjustment.amount)
    t.subtransactions.append(adjustment)
    assert yap.utils.equalish(t.amount, sum(s.amount for s in t.subtransactions))


def update():
    update_rest()
    update_gui()


def update_rest():
    yap.utils.log_info('Updating %s transactions via YNAB REST API' % len(transactions_to_rest_update))
    for t in transactions_to_rest_update:
        yap.utils.log_info(t)
        yap.ynab.api_client.update(t)
    yap.utils.log_info(yap.utils.separator)


def annotate_for_locating(t):
    yap.utils.log_debug('annotate_for_locating', t)
    old_memo = t.memo
    t.memo = t.id
    return old_memo


def update_gui():
    n =len(transactions_to_gui_update)
    yap.utils.log_debug('update_gui', n)
    if not transactions_to_gui_update:
        return
    yap.utils.log_info('Updating %s transactions via YNAB webapp' % n)
    for t in transactions_to_gui_update:
        # Ensures that we can find it in the gui
        if len(t.subtransactions) <= 1:
            yap.utils.log_debug('Warning: updating via gui with %s subtransactions' % len(t.subtransactions), t)
        old_memo = annotate_for_locating(t)
        yap.ynab.api_client.update(t)
        t.memo = old_memo
        add_adjustment_subtransaction(t)
    yap.ynab.gui_client.load_gui()
    yap.ynab.gui_client.enter_all_transactions(transactions_to_gui_update)
    yap.utils.log_info(yap.utils.separator)
