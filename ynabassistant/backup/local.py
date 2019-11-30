import jsonpickle
import os
import glob
import datetime
import functools

import ynab_api

import ynabassistant as ya

# Local Backup


def get_backup_path(t, n):
    name = '%s-%s-%s.jsonpickle' % (ya.settings.start_time, t, n)
    return os.path.join(ya.settings.backup_dir, name)


@ya.utils.listy
def save(x, n):
    assert len(set(map(type, x))) == 1
    t = type(x[0])
    path = get_backup_path(t, n)
    with open(path, 'w+') as f:
        f.write(jsonpickle.encode(x))
    return path


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


def load(t, n, predicates=()):
    loaded = load_path(get_backup_path(t, n))
    return ya.utils.multi_filter(predicates, loaded)


def load_transactions(n, predicates=()):
    return load(ynab_api.TransactionDetail, n, predicates)


def load_account_transactions(account_name, n, predicates=()):
    return load_transactions(n, (lambda t: t.account_name == account_name,) + predicates)


def load_path(path):
    ya.utils.log_debug('loading', path)
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        raw = f.read()
        decoded = jsonpickle.decode(raw)
        return decoded


def save_and_log(f):
    f.n_calls = 0

    @functools.wraps(f)
    def save_and_log_f(*args, **kwargs):
        ya.utils.log_debug(*args, **kwargs)
        f.n_calls += 1
        ret = f(*args, **kwargs)
        if not ret:
            ya.utils.log_debug('null ret', ret)
            return
        ya.utils.log_debug(*ret)
        ya.backup.local.save(ret, f.n_calls)
        return ret
    return save_and_log_f
