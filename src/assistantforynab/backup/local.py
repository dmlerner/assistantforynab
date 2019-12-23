import jsonpickle
import collections
import os
import glob
import datetime
import functools

import ynab_api

from ynabassistant import settings, backup
from ynabassistant.utils import utils

# Local Backup

versions = collections.defaultdict(lambda: -1)


def get_backup_path(t, n):
    name = '%s-%s-%s.jsonpickle' % (settings.start_time, t, n)  # TODO: DRY
    return os.path.join(settings.backup_dir, name)


@utils.listy
def store(x):
    assert len(set(map(type, x))) == 1
    t = type(x[0])
    versions[t] += 1
    path = get_backup_path(t, versions[t])
    with open(path, 'w+') as f:
        f.write(jsonpickle.encode(x))
    return path


def load_before(t, timestamp=settings.start_time):
    ''' Load the newest file made before timestamp '''
    assert isinstance(timestamp, datetime.datetime)
    paths = glob.glob(settings.backup_dir + '/*-' + str(t) + '-*.jsonpickle')
    for path in sorted(paths, reverse=True):
        filename = path.replace(settings.backup_dir + '/', '')
        file_timestamp = filename[:filename.index('-<')]
        if file_timestamp < str(timestamp):
            break
    else:
        assert False
        # return []
    utils.log_info('Reloading from %s' % file_timestamp)
    return load_path(path)


def load(t, n=None, predicates=()):
    utils.log_debug('load', t, n)
    if n is None:
        return sum(map(lambda n: load(t, n), range(versions[t] + 1)), [])
    if n == -1:  # ie, most recent
        n = versions[t]
    loaded = load_path(get_backup_path(t, n))
    return utils.multi_filter(predicates, loaded)


def load_transactions(n=None, predicates=()):
    return load(ynab_api.TransactionDetail, n, predicates)


def load_account_transactions(account_name, n=None, predicates=()):
    return load_transactions(n, (lambda t: t.account_name == account_name,) + predicates)


def load_path(path):
    utils.log_debug('loading', path)
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        raw = f.read()
        decoded = jsonpickle.decode(raw)
        return decoded


def save(f):

    @functools.wraps(f)
    def _f(*args, **kwargs):
        utils.log_debug(*args, **kwargs)
        ret = f(*args, **kwargs)
        if not ret:
            utils.log_debug('null ret', ret)
            return
        utils.log_debug(*ret)
        backup.local.store(ret)
        return ret
    return _f


def get_accounts():
    return load_before(ynab_api.Account)


def get_transactions():
    return load_before(ynab_api.TransactionDetail)


def get_category_groups():
    return load_before(ynab_api.CategoryGroupWithCategories)


def get_payees():
    return load_before(ynab_api.Payee)
