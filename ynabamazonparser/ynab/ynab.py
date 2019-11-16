from copy import deepcopy

from ynabamazonparser import utils
from ynabamazonparser.ynab import api_client, gui_client
from ynabamazonparser.ocnfig import settings

# Needed iff changing subtransactions
# I'm abusing subtransactions field by storing [ynab.Transactions]
# Instead of [official api subtransaction]
transactions_to_gui_update = []

# Any changes to subtransactions are ignored
transactions_to_rest_update = []


def add_adjustment_subtransaction(t):
    ''' Ensures that the sum of subtransaction prices equals the transaction amount '''
    subtransaction_total = sum(s.amount for s in t.subtransactions)
    if utils.equalish(subtransaction_total, t.amount):
        return
    adjustment = deepcopy(t)
    adjustment.subtransactions = []
    adjustment.memo = 'Split transaction adjustment'
    adjustment.amount = t.amount - subtransaction_total
    adjustment.category_name = settings.default_category  # TODO
    utils.log('Warning: subtransactions do not add up, by $%s' % adjustment.amount)
    t.subtransactions.append(t)
    assert utils.equalish(t.amount, sum(s.amount for s in t.subtransactions))


def update():
    update_rest()
    update_gui()


def update_rest():
    utils.log('Updating YNAB via REST')
    for t in transactions_to_rest_update:
        api_client.update(t)
    utils.log(utils.separator)


def annotate_for_locating(t):
    t.memo = t.id + t.memo


def remove_locating_annotation(t):
    assert t.memo.startswith(t.id)
    t.memo = t.memo[len(t.id):]


def update_gui():
    utils.log('Updating YNAB via GUI')
    for t in transactions_to_gui_update:
        # Ensures that we can find it in the gui
        if len(t.subtransactions) <= 1:
            utils.log('Warning: no good reason to update via gui with <= 1 subtransaction')
        annotate_for_locating(t)
        api_client.update(t)
        remove_locating_annotation(t)
        add_adjustment_subtransaction(t)
    gui_client.load_gui()
    for t in transactions_to_gui_update:
        gui_client.update(t)
    utils.log(utils.separator)
