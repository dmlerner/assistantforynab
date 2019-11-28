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


def load(t, predicates=()):
    ''' Load the current session's backup '''
    loaded = load_path(get_backup_path(t))
    return list(ya.utils.multi_filter(predicates, loaded))


def load_transactions(predicates=()):
    return load(ynab_api.TransactionDetail, predicates)


def load_account_transactions(account_name, predicates=()):
    return load_transactions((lambda t: t.account_name == account_name,) + predicates)


def load_path(path):
    ya.utils.log_debug('loading', path)
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        raw = f.read()
        decoded = jsonpickle.decode(raw)
        return decoded
