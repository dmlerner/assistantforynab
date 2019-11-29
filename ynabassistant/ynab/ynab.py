import copy
import collections
import ynab
import ynab_api
import ynabassistant as ya

# Needed iff changing subtransactions
gui_queue = collections.defaultdict(dict)  # mode: { id: TransactionDetail }

# Any changes to subtransactions are ignored
rest_queue = collections.defaultdict(dict)  # mode: { id: TransactionDetail }

# set memo via rest; search and delete all via GUI
transaction_delete_queue = {}  # { id: TransactionDetail }
account_delete_queue = {}  # { id: Accountsomething... }


def add_adjustment_subtransaction(t):
    ''' Ensures that the sum of subtransaction prices equals the transaction amount '''
    ya.utils.log_debug('add_adjustment_subtransaction', t)
    if not t.subtransactions:
        return
    amount = ynab.utils.calculate_adjustment(t)
    if not amount:
        return
    adjustment = copy.deepcopy(t.subtransactions[0])
    adjustment.memo = 'Split transaction adjustment'
    adjustment.amount = amount
    adjustment.category_name = ya.settings.default_category  # TODO
    ya.utils.log_info('Warning, adjusting: subtransactions do not add up, by $%s' % -ynab.utils.amount(adjustment))
    t.subtransactions.append(adjustment)
    assert ya.utils.equalish(t.amount, sum(s.amount for s in t.subtransactions))


def do():
    do_delete()
    do_rest()
    do_gui()


def do_rest():
    ya.utils.log_debug('do_rest', rest_queue)
    if not rest_queue:
        return
    for mode, ts in rest_queue.items():
        ya.utils.log_info('%s %s transactions via YNAB REST API' % (mode, len(ts)))
        ya.utils.log_debug(mode, *ts)
        copied = copy.deepcopy(ts)  # TODO: do we need copy?
        for t in copied:  # TODO: surely we don't need this
            if t.subtransactions:
                t.subtransactions = []
                t.category_id = None
                t.category_name = None

        rest_modes[mode](copied)
        ya.utils.log_info(ya.utils.separator)
    rest_queue.clear()


def annotate_for_locating(t):
    ya.utils.log_debug('annotate_for_locating', t)
    old_memo = t.memo
    t.memo = t.id
    return old_memo


def do_gui():
    ya.utils.log_debug('do_gui', gui_queue)
    if not gui_queue:
        return
    old_memos = []
    for mode, ts in gui_queue.items():
        ya.utils.log_info('%s %s transactions via YNAB webapp' % (mode, len(ts)))
        ya.utils.log_debug(mode, *ts)
        assert mode != 'delete'
        for t in ts:
            if len(t.subtransactions) <= 1:
                ya.utils.log_debug('Warning: no good reason to update via gui with %s subtransaction(s)' %
                                   len(t.subtransactions), t)
            # Ensures that we can find it in the gui
            old_memos.append(annotate_for_locating(t))
        rest_modes[mode](ts)
        for m, t in zip(old_memos, ts):
            t.memo = m
            add_adjustment_subtransaction(t)
        ynab.gui_client.enter_all_transactions(ts)
        ya.utils.log_info(ya.utils.separator)
    gui_queue.clear()
    ya.utils.gui.quit()


def check_payee(st, payees):
    ya.ynab.utils.type_assert_st(st)
    assert not st.payee_id or st.payee_id in payees
    # Need get because this is a field that isn't on the ynab_api model
    # I just add it for gui_client convenience in amazon.amazon
    if st.payee_id and st.__dict__.get('payee_name'):
        assert payees[st.payee_id].name == st.payee_name
    if isinstance(st, ynab_api.TransactionDetail):
        [check_payee(s, payees) for s in st.subtransactions]


def check_category(st, categories):
    ya.ynab.utils.type_assert_st(st)
    assert not st.category_id or st.category_id in categories
    if st.category_id and st.__dict__.get('category_name'):
        assert categories[st.category_id].name == st.category_name
    if isinstance(st, ynab_api.TransactionDetail):
        [check_category(s, categories) for s in st.subtransactions]


def queue(ts, mode, payees, categories):
    ya.utils.log_debug('queue', ts, mode, payees, categories)
    assert mode in rest_modes
    if type(ts) not in (tuple, list):
        ts = [ts]
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
    for t in ts:
        if payees is not None:  # TODO: check them all at once. Or even like actually use this...
            check_payee(t, payees)
        if categories is not None:
            check_category(t, categories)
        enqueue((gui_queue if t.subtransactions else rest_queue)[mode], t)


def queue_create(ts, payees=None, categories=None):
    queue(ts, 'create', payees=None, categories=None)


def queue_update(ts, payees=None, categories=None):
    queue(ts, 'update', payees, categories)


def enqueue(xs, queue):
    if not xs:
        return
    if isinstance(xs, dict):
        xs = list(xs.values())
    elif type(xs) not in (list, tuple):
        xs = list(xs)
    null_id = filter(lambda x: x.id is None, xs)
    has_id = filter(lambda x: x.id is not None, xs)
    assert len(set(map(lambda x: x.id, has_id))) == len(has_id)
    queue.update(ya.utils.by(xs, lambda x: x.id))
    queue[None].extend(null_id)


def queue_delete_transactions(ts):
    enqueue(ts, transaction_delete_queue)


def queue_delete_accounts(accounts):
    enqueue(accounts, account_delete_queue)


def do_delete_accounts():
    ya.ynab.gui_client.delete_accounts(account_delete_queue.values())


delete_key = 'DELETEMEDELETEMEDELETEME'


def do_delete_transactions():
    ya.utils.log_debug('delete', transaction_delete_queue)
    if not transaction_delete_queue:
        return
    ya.utils.log_info('Set deletion memo on %s transactions via YNAB REST API' % len(transaction_delete_queue))
    for t in transaction_delete_queue.values():
        t.memo = delete_key
    ynab.api_client.update_transactions(transaction_delete_queue.values())
    ya.utils.log_info('delete %s transactions via YNAB webapp' % len(transaction_delete_queue))
    ynab.gui_client.delete_transactions()
    transaction_delete_queue.clear()


def do_delete():
    for a in account_delete_queue.values():
        queue_delete_transactions(ya.assistant.utils.get_transactions(a.name))
    do_delete_transactions()
    do_delete_accounts()
    ya.utils.gui.quit()


def queue_move_transactions(ts, account):
    ya.utils.log_debug('queue_move_transactions', *ts, account)
    assert ya.Assistant.accounts.get(account.id)
    queue_copy_to_account(ts, account)
    queue_delete_transactions(ts)


def modify_transaction_for_moving(t, account):
    t.account_name = account.name  # matters to gui but not rest
    t.account_id = account.id
    t.import_id = None
    for s in t.subtransactions:
        # s.category_name = ya.settings.default_category # TODO: surely we just want to leave it alone...
        if s.payee_id:
            assert s.payee_id in ya.Assistant.payees
            s.payee_name = ya.Assistant.payees[s.payee_id].name


def queue_copy_to_account(ts, account):
    ya.utils.log_debug('queue_copy_to_account', *ts, account)
    assert ya.Assistant.accounts.get(account.id)
    to_copy = copy.deepcopy(ts)
    for t in to_copy:
        modify_transaction_for_moving(t, account)
    ya.utils.log_debug('to_copy', *to_copy)
    ya.ynab.queue_create(to_copy)


def clone_account(source_account, target_name):
    assert ya.Assistant.accounts.get(source_account.id)
    target_account = ya.assistant.utils.get_account(target_name)
    if target_account:
        queue_clear_account(target_account)
    else:
        add_unlinked_account(target_name)
    ts = ya.assistant.utils.get_transactions(source_account.name)
    queue_copy_to_account(ts, target_name)


def queue_clear_account(account):
    queue_delete_transactions(ya.assistant.utils.get_transactions(account.name))


def add_unlinked_account(account_name, balance=0, account_type='credit'):
    ya.ynab.gui_client.add_unlinked_account(account_name, balance, account_type)
    ya.utils.gui.quit()


rest_modes = {'create': ynab.api_client.create_transactions,
              'update': ynab.api_client.update_transactions,
              }

no_check_configuration = ynab_api.Configuration()
no_check_configuration.client_side_validation = False
