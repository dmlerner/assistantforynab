from copy import deepcopy
import collections
import ynab
import ynab_api
import ynabassistant as ya

# Needed iff changing subtransactions
gui_queue = collections.defaultdict(list)  # mode: [TransactionDetail]

# Any changes to subtransactions are ignored
rest_queue = collections.defaultdict(list)  # mode: [TransactionDetail]


def add_adjustment_subtransaction(t):
    ''' Ensures that the sum of subtransaction prices equals the transaction amount '''
    ya.utils.log_debug('add_adjustment_subtransaction', t)
    if not t.subtransactions:
        return
    amount = ynab.utils.calculate_adjustment(t)
    if not amount:
        return
    adjustment = deepcopy(t.subtransactions[0])
    adjustment.memo = 'Split transaction adjustment'
    adjustment.amount = amount
    adjustment.category_name = ya.settings.default_category  # TODO
    ya.utils.log_info('Warning, adjusting: subtransactions do not add up, by $%s' % -ynab.utils.amount(adjustment))
    t.subtransactions.append(adjustment)
    assert ya.utils.equalish(t.amount, sum(s.amount for s in t.subtransactions))


def do():
    do_rest()
    do_gui()


def do_rest():
    ya.utils.log_debug('do_rest', rest_queue)
    if not rest_queue:
        return
    for mode, ts in rest_queue.items():
        ya.utils.log_info('%s %s transactions via YNAB REST API' % (mode, len(ts)))
        ya.utils.log_debug(mode, *ts)
        copied = deepcopy(ts)
        for t in copied:
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
        ynab.gui_client.load_gui()
        ynab.gui_client.enter_all_transactions(ts)
        ya.utils.log_info(ya.utils.separator)
    gui_queue.clear()


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
    assert mode in rest_modes
    if type(ts) not in (tuple, list):
        ts = [ts]
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
    for t in ts:
        if payees is not None:
            check_payee(t, payees)
        if categories is not None:
            check_category(t, categories)
        (gui_queue if t.subtransactions else rest_queue)[mode].append(t)


def queue_create(ts, payees=None, categories=None):
    queue(ts, 'create', payees=None, categories=None)


def queue_update(ts, payees=None, categories=None):
    queue(ts, 'update', payees, categories)


rest_modes = {'create': ynab.api_client.create_transactions,
              'update': ynab.api_client.update_transactions}

no_check_configuration = ynab_api.Configuration()
no_check_configuration.client_side_validation = False
