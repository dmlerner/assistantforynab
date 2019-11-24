import jsonpickle
import os
import glob
import datetime

import ynab_api

import ynabassistant as ya

# Local Backup


def get_backup_path(t):
    name = str(ya.settings.start_time) + '-' + str(t) + '.jsonpickle'
    return os.path.join(ya.settings.backup_dir, name)


def save(x):
    if type(x) not in (tuple, list):
        x = [x]
    assert len(set(map(type, x))) == 1
    t = type(x[0])
    existing = load(t)
    with open(get_backup_path(t), 'w+') as f:
        f.write(jsonpickle.encode(existing + x))


def load_before(t, timestamp=ya.settings.start_time):
    ''' Load the newest file made before timestamp '''
    assert isinstance(timestamp, datetime.datetime)
    paths = glob.glob(ya.settings.backup_dir + '/*-' + str(t) + '.jsonpickle')
    for path in sorted(paths, reverse=True):
        filename = path.replace(ya.settings.backup_dir + '/', '')
        file_timestamp = filename[:filename.index('-<')]
        if file_timestamp < str(timestamp):
            break
    else:
        assert False
        # return []
    ya.utils.log_info('Reloading from %s' % file_timestamp)
    return load_path(path)


def load(t):
    ''' Load the current session's backup '''
    return load_path(get_backup_path(t))


def load_path(path):
    ya.utils.log_debug('loading', path)
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        raw = f.read()
        decoded = jsonpickle.decode(raw)
        return decoded

# Remote backup


def diff_with_backup(predicates=(), timestamp=ya.settings.start_time, order='first'):
    backup_transactions = list(ya.utils.multi_filter(predicates, load_before(ynab_api.TransactionDetail, timestamp)))

    def key(t):
        return t.id

    # Get the first copy of the transaction saved
    # So that eg default arguments restore state at start of prior run
    unique = ya.utils.by(get_unique(backup_transactions, key, order), key)
    unique_keys = set(unique.keys())

    ya.assistant.Assistant.load_ynab_data()
    current_transactions = ya.utils.by(
        ya.utils.multi_filter(
            predicates,
            ya.assistant.Assistant.transactions.values()),
        key)
    current_keys = set(current_transactions.keys())
    ya.utils.debug()
    modified = unique_keys.intersection(current_keys)
    deleted = unique_keys - current_keys
    added = current_keys - unique_keys
    ya.utils.log_info(
        'Found %s modified, %s deleted, %s added transactions' %
        (len(modified), len(deleted), len(added)))
    return [list(filter(lambda t: t.id in x, backup_transactions)) for x in (modified, deleted, added)]


def restore_account_transactions(name=ya.settings.account_name):
    restore_transactions((lambda t: ya.utils.newer_than(t.date), lambda t: t.account_name == name))


def restore_transactions(predicates=(), timestamp=ya.settings.start_time, order='first', confirm=True):
    modified, deleted, added = diff_with_backup(predicates, timestamp, order)
    ya.utils.log_debug('before')
    ya.utils.log_debug(modified)
    ya.utils.log_debug(deleted)
    ya.utils.log_debug(added)
    if confirm and not do_confirm(modified, deleted, added):
        return
    ya.ynab.queue_update(modified)
    # ya.ynab.queue_delete(added)
    # ya.ynab.queue_create(deleted)  # TODO: is this really just an update of deleted flag?
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


'''
def upload_to_new_account(annotated):
    ya.utils.log_info('upload_to_new_account')
    to_upload = copy.deepcopy(annotated)
    account_ids = [id for (id, ac) in ya.assistant.Assistant.accounts.items() if ac.name == ya.settings.account_name]
    assert len(account_ids) == 1
    account_id = account_ids.pop()
    for t in to_upload:
        t.account_name = ya.settings.account_name  # matters to gui but not rest
        t.account_id = account_id
        t.import_id = None
        for s in t.subtransactions:
            if s.payee_id:
                assert s.payee_id in ya.assistant.Assistant.payees
                s.payee_name = ya.assistant.Assistant.payees[s.payee_id].name
    ya.utils.log_info('to_upload', *to_upload)
    ya.ynab.queue_create(to_upload)
    ya.ynab.do()


def to_tuple(t):
    return t.amount, t.approved, t.category_id, t.category_name, t.cleared, t.date, \
        t.deleted, t.flag_color, t.memo, t.payee_id, t.payee_name, t.transfer_account_id


def sub_to_tuple(s):
    return s.amount, s.category_id, s.deleted, s.memo, s.payee_id, s.transfer_account_id


def diff(ts1, ts2, tupler):
    tuple_ts1 = set(map(tupler, ts1))
    tuple_ts2 = set(map(tupler, ts2))
    return tuple_ts1 - tuple_ts2, tuple_ts2 - tuple_ts1
'''
