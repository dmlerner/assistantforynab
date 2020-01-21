import time
import collections
import ynab_api

import assistantforynab as afy
from assistantforynab.utils import utils, gui
from . import api_client, gui_client
from .utils import calculate_adjustment, get_amount, type_assert_st

# Needed if changing subtransactions
gui_queue = collections.defaultdict(dict)  # mode: { id: TransactionDetail }

# Any changes to subtransactions are ignored
rest_queue = collections.defaultdict(dict)  # mode: { id: TransactionDetail }

# set memo via rest; search and delete all via GUI
transaction_delete_queue = {}  # { id: TransactionDetail }
account_delete_queue = {}  # { id: Accountsomething.. }


def add_adjustment_subtransaction(t):
    ''' Ensures that the sum of subtransaction prices equals the transaction amount '''
    utils.log_debug('add_adjustment_subtransaction', t)
    if not t.subtransactions:
        return
    amount = calculate_adjustment(t)
    if not amount:
        return
    adjustment = utils.copy(t.subtransactions[0])
    adjustment.memo = 'Split transaction adjustment'
    adjustment.amount = amount
    adjustment.category_name = afy.settings.default_category  # TODO
    utils.log_info('Warning, adjusting: subtransactions do not add up, by $%s' % -get_amount(adjustment))
    t.subtransactions.append(adjustment)
    assert utils.equalish(t.amount, sum(s.amount for s in t.subtransactions))


def do():
    do_delete()
    do_rest()
    do_gui()


def do_rest():
    utils.log_debug('do_rest', rest_queue)
    if not rest_queue:
        return
    for mode, ts in rest_queue.items():
        utils.log_info('%s %s transactions via YNAB REST API' % (mode, len(ts)))
        utils.log_debug(mode, ts)
        '''
        copied = copy.deepcopy(ts)  # TODO: do we need copy?
        for t in copied:  # TODO: surely we don't need this
            if t.subtransactions:
                t.subtransactions = []
                t.category_id = None
                t.category_name = None
        rest_modes[mode](copied)
                '''

        rest_modes[mode](ts)
        utils.log_info(utils.separator)
    rest_queue.clear()


def annotate_for_locating(t):
    utils.log_debug('annotate_for_locating', t)
    old_memo = t.memo
    t.memo = t.id
    return old_memo


def do_gui():
    utils.log_debug('do_gui', gui_queue)
    if not gui_queue:
        return
    old_memos = []
    for mode, ts in gui_queue.items():
        utils.log_info('%s %s transactions via YNAB webapp' % (mode, len(ts)))
        utils.log_debug(mode, ts)
        for t in ts.values():  # TODO: can this be simplified?
            if len(t.subtransactions) <= 1:
                utils.log_debug('Warning: no good reason to update via gui with %s subtransaction(s)' %
                                len(t.subtransactions), t)
            # Ensures that we can find it in the gui
            old_memos.append(annotate_for_locating(t))
        rest_modes[mode](ts)
        for m, t in zip(old_memos, ts.values()):  # simplify out the .values? listy?
            t.memo = m
            add_adjustment_subtransaction(t)
        gui_client.enter_all_transactions(ts)
        utils.log_info(utils.separator)
    gui_queue.clear()
    gui.quit()


def check_payee(st, payees):
    utils.log_debug('check_payee', st)
    type_assert_st(st)
    assert not st.payee_id or st.payee_id in payees
    # Need get because this is a field that isn't on the api model
    # I just add it for gui_client convenience in amazon.amazon
    if st.payee_id and st.__dict__.get('payee_name'):
        assert payees[st.payee_id].name == st.payee_name
    if isinstance(st, ynab_api.TransactionDetail):
        [check_payee(s, payees) for s in st.subtransactions]


def check_category(st, categories):
    utils.log_debug('check_category', st)
    type_assert_st(st)
    assert not st.category_id or st.category_id in categories
    if st.category_id and st.__dict__.get('category_name'):
        assert categories[st.category_id].name == st.category_name
    if isinstance(st, ynab_api.TransactionDetail):
        [check_category(s, categories) for s in st.subtransactions]


def trim_memo_length(t):
    utils.log_debug('trim_memo_length', t)
    type_assert_st(t)
    if t.memo is not None:
        t.memo = t.memo[:200]
        if isinstance(t, ynab_api.TransactionDetail):
            [trim_memo_length(st) for st in t.subtransactions]
    return t


@utils.listy
def queue(ts, mode, payees, categories):
    utils.log_debug('queue', ts, mode)
    assert mode in rest_modes
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
    for t in ts:
        if payees is not None:  # TODO: check them all at once. Or even like actually use this..
            check_payee(t, payees)
        if categories is not None:
            check_category(t, categories)
        t = trim_memo_length(t)
        enqueue(t, (gui_queue if t.subtransactions else rest_queue)[mode])


@utils.listy
def queue_create(ts, payees=None, categories=None):
    utils.log_debug('queue_create', ts)
    queue(ts, 'create', payees=None, categories=None)


@utils.listy
def queue_update(ts, payees=None, categories=None):
    utils.log_debug('queue_update', ts)
    queue(ts, 'update', payees, categories)


@utils.listy
def enqueue(xs, queue):
    utils.log_debug('enqueue', xs, queue)
    xs = utils.copy(xs)

    has_id = list(filter(lambda x: x.id is not None, xs))
    assert len(set(map(lambda x: x.id, has_id))) == len(has_id)
    queue.update(utils.by(xs, lambda x: x.id))

    null_id = list(filter(lambda x: x.id is None, xs))
    if null_id:
        if None not in queue:
            queue[None] = []
        queue[None].extend(null_id)


@utils.listy
def queue_delete_transactions(ts):
    utils.log_debug('queue_delete_transactions', ts)
    enqueue(ts, transaction_delete_queue)


@utils.listy
def queue_delete_accounts(accounts):
    utils.log_debug('queue_delete_accounts', accounts)
    enqueue(accounts, account_delete_queue)


def do_delete_accounts(wait=30, sleep=5):
    if not account_delete_queue:
        return
    utils.log_debug('do_delete_accounts')
    gui_client.delete_accounts(account_delete_queue)
    start = time.time()
    while time.time() - start < wait:  # TODO: consider fixing this instead or also in api_client
        afy.Assistant.download_ynab(accounts=True)
        utils.log_debug(
            'account keys, delete queue keys', set(
                afy.Assistant.accounts.ids), set(
                account_delete_queue.keys()))
        if set(afy.Assistant.accounts.ids).intersection(set(account_delete_queue.keys())):
            time.sleep(sleep)
        else:
            account_delete_queue.clear()
            return
    assert False


delete_key = 'DELETEMEDELETEMEDELETEME'


def do_delete_transactions():
    utils.log_debug('do_delete_transactions', transaction_delete_queue)
    if not transaction_delete_queue:
        return
    utils.log_info('Set deletion memo on %s transactions via YNAB REST API' % len(transaction_delete_queue))
    for t in transaction_delete_queue.values():
        t.memo = delete_key
    api_client.update_transactions(transaction_delete_queue)
    utils.log_info('delete %s transactions via YNAB webapp' % len(transaction_delete_queue))
    gui_client.delete_transactions()
    transaction_delete_queue.clear()


def do_delete():
    utils.log_debug('do_delete')
    for a in account_delete_queue.values():
        queue_delete_transactions(afy.Assistant.transactions.by_name(a.name))
    do_delete_transactions()
    do_delete_accounts()
    gui.quit()


@utils.listy
def queue_move_transactions(ts, account):
    utils.log_debug('queue_move_transactions', ts, account)
    assert afy.Assistant.accounts.get(account.id)
    queue_copy_to_account(ts, account)
    queue_delete_transactions(ts)


def modify_transaction_for_moving(t, account):
    t.account_name = account.name  # matters to gui but not rest
    t.account_id = account.id
    t.import_id = None
    for s in t.subtransactions:
        # s.category_name = afy.settings.default_category # TODO: surely we just want to leave it alone..
        if s.payee_id:
            assert s.payee_id in afy.Assistant.payees.ids
            s.payee_name = afy.Assistant.payees.get(s.payee_id).name


@utils.listy
def queue_copy_to_account(ts, account):
    utils.log_debug('queue_copy_to_account', ts, account)
    assert afy.Assistant.accounts.get(account.id)
    to_copy = utils.copy(ts)
    for t in to_copy:
        modify_transaction_for_moving(t, account)
    utils.log_debug('to_copy', to_copy)
    queue_create(to_copy)


def queue_clone_account(source_account, target_name):
    utils.log_debug('queue_clone_account', source_account, target_name)
    assert afy.Assistant.accounts.get(source_account.id)
    target_account = afy.Assistant.accounts.by_name(target_name)
    if target_account:
        queue_clear_account(target_account)
    else:
        add_unlinked_account(target_name)
        time.sleep(3)
        afy.Assistant.download_ynab(accounts=True)
        target_account = afy.Assistant.accounts.by_name(target_name)
    ts = afy.Assistant.transactions.by_name(source_account.name)
    queue_copy_to_account(ts, target_account)


def queue_clear_account(account):
    utils.log_debug('queue_clear_account', account)
    queue_delete_transactions(afy.Assistant.transactions.by_name(account.name))


def add_unlinked_account(account_name, balance=0, account_type='credit'):
    utils.log_debug('add_unlinked_account', account_name, balance, account_type)
    gui_client.add_unlinked_account(account_name, balance, account_type)
    gui.quit()
    afy.Assistant.download_ynab(accounts=True)
    start = time.time()
    while time.time() - start < 30:  # TODO: generic retrier
        new_account = afy.Assistant.accounts.by_name(account_name)
        if new_account:
            return new_account
    assert False


rest_modes = {'create': api_client.create_transactions,
              'update': api_client.update_transactions,
              }

no_check_configuration = ynab_api.Configuration()
no_check_configuration.client_side_validation = False
