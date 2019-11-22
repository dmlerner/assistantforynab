from copy import deepcopy

import ynabassistant as ya
import ynab

# Needed iff changing subtransactions
# I'm abusing subtransactions field by storing [ynab.Transactions]
# Instead of [official api subtransaction]
transactions_to_gui_update = []

# Any changes to subtransactions are ignored
transactions_to_rest_update = []


def add_adjustment_subtransaction(t):
    ''' Ensures that the sum of subtransaction prices equals the transaction amount '''
    ya.utils.log_debug('add_adjustment_subtransaction', t)
    if not t.subtransactions:
        return
    amount = ynab.utils.calculate_adjustment(t)
    if not amount:
        return
    adjustment = deepcopy(t.subtransactions[0])
    adjustment.subtransactions = []
    adjustment.memo = 'Split transaction adjustment'
    adjustment.amount = amount
    adjustment.category_name = ya.settings.default_category  # TODO
    ya.utils.log_info('Warning, adjusting: subtransactions do not add up, by $%s' % -ynab.utils.amount(adjustment))
    t.subtransactions.append(adjustment)
    assert ya.utils.equalish(t.amount, sum(s.amount for s in t.subtransactions))


def update():
    update_rest()
    update_gui()


def update_rest():
    ya.utils.log_debug('update_rest', transactions_to_rest_update)
    if not transactions_to_rest_update:
        return
    ya.utils.log_info('Updating %s transactions via YNAB REST API' % len(transactions_to_rest_update))
    ya.utils.log_info(transactions_to_rest_update)
    ynab.api_client.update_transactions(transactions_to_rest_update)
    ya.utils.log_info(ya.utils.separator)


def annotate_for_locating(t):
    ya.utils.log_debug('annotate_for_locating', t)
    old_memo = t.memo
    t.memo = t.id
    return old_memo


def update_gui():
    ya.utils.log_debug('update_gui', transactions_to_gui_update)
    if not transactions_to_gui_update:
        return
    ya.utils.log_info('Updating %s transactions via YNAB webapp' % len(transactions_to_gui_update))
    old_memos = []
    for t in transactions_to_gui_update:
        if len(t.subtransactions) <= 1:
            ya.utils.log_debug('Warning: no good reason to update via gui with %s subtransaction(s)' % len(t.subtransactions), t)
        # Ensures that we can find it in the gui
        old_memos.append(annotate_for_locating(t))
    ynab.api_client.update_transactions(transactions_to_gui_update)
    for m, t in zip(old_memos, transactions_to_gui_update):
        t.memo = m
        add_adjustment_subtransaction(t)
    ynab.gui_client.load_gui()
    ynab.gui_client.enter_all_transactions(transactions_to_gui_update)
    ya.utils.log_info(ya.utils.separator)
