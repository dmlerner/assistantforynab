import copy
import ynab_api

import ynabassistant as ya


def diff_with_backup(predicates, timestamp=ya.settings.start_time, order='first'):
    all_backup_transactions = ya.backup.local.load_before(ynab_api.TransactionDetail, timestamp)
    matching = ya.utils.multi_filter(predicates, all_backup_transactions)

    def key(t):
        return t.id

    # Get the first copy of the transaction saved
    # So that eg default arguments restore state at start of prior run
    unique = ya.utils.by(get_unique(matching, key, order), key)
    unique_keys = set(unique.keys())

    ya.Assistant.download_ynab(transactions=True)  # TODO: can I get away with this?
    current_transactions = ya.utils.by(
        ya.utils.multi_filter(
            predicates,
            ya.Assistant.transactions.values()),
        key)
    current_keys = set(current_transactions.keys())
    ya.utils.debug()
    modified = unique_keys.intersection(current_keys)
    deleted = unique_keys - current_keys
    added = current_keys - unique_keys
    ya.utils.log_info(
        'Found %s modified, %s deleted, %s added transactions' %
        (len(modified), len(deleted), len(added)))
    return [list(filter(lambda t: t.id in x, matching)) for x in (modified, deleted, added)]


def restore_account_transactions(name=ya.settings.account_name):
    # restores only transactions newer than default of 30 days
    restore_transactions((lambda t: ya.utils.newer_than(t.date), lambda t: t.account_name == name))


def restore_transactions(predicates, timestamp=ya.settings.start_time, order='first', confirm=True):
    modified, deleted, added = diff_with_backup(predicates, timestamp, order)
    ya.utils.log_debug('before')
    ya.utils.log_debug(modified)
    ya.utils.log_debug(deleted)
    ya.utils.log_debug(added)
    if confirm and not do_confirm(modified, deleted, added):
        return
    ya.ynab.queue_update(modified)
    # ya.ynab.queue_delete(added) # TODO: is this just an update by setting delete = true?
    # ya.ynab.queue_create(deleted)  # TODO: is this really just an update of deleted = false?
    ya.ynab.do()
    modified, deleted, added = diff_with_backup(predicates, timestamp, order)
    ya.utils.log_debug('after')
    ya.utils.log_debug(modified)
    ya.utils.log_debug(deleted)
    ya.utils.log_debug(added)
    assert not (modified or deleted or added)  # TODO: retry?


def do_confirm(modified, deleted, added):
    ya.utils.log_info("Nah, fuck confirming")
    return True


def get_unique(x, key, order='first'):
    assert order in ('first', 'last', 'unique')
    grouped = ya.utils.group_by(x, key)
    if order == 'unique':
        assert all(len(v) == 1 for v in grouped.values())
    index = 0 if order == 'first' else -1
    return [grouped[k][index] for k in grouped]


def copy_to_account(ts, account_name):
    ya.utils.log_debug('copy_to_account', *ts)
    to_upload = copy.deepcopy(ts)
    account_id = ya.assistant.utils.get_account(account_name).id
    for t in to_upload:
        t.account_name = account_name  # matters to gui but not rest
        t.account_id = account_id
        t.import_id = None
        for s in t.subtransactions:
            s.category_name = ya.settings.default_category
            if s.payee_id:
                assert s.payee_id in ya.Assistant.payees
                s.payee_name = ya.Assistant.payees[s.payee_id].name
    ya.utils.log_debug('to_upload', *to_upload)
    ya.ynab.queue_create(to_upload)
    ya.ynab.do()


'''
    # ynab_api will create payee if needed when id is null
    # payee_name doesn't actually exist on subtransaction
    # but rest_client ignores subtransactions
    # and it's useful to gui_client
    st.payee_name = get_payee_name(i)
    st.payee_id = None

    # category_name exists on transaction, but not savetransaction
    # similarly, ignored by rest_client but used by gui_client
    st.category_name = get_category_name(i)
    category = ya.assistant.utils.get_account(st.category_name)
    st.category_id = category.id if category else None
'''
