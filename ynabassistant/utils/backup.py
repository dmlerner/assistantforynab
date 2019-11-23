import jsonpickle
import os
import glob
import datetime

import ynabassistant as ya


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


def load_on_or_before(t, timestamp=ya.settings.start_time):
    ''' Load the newest file made on or before timestamp '''
    assert isinstance(timestamp, datetime.datetime)
    paths = glob.glob(ya.settings.backup_dir + '/*-' + str(t) + '.jsonpickle')
    for path in sorted(paths, reverse=True):
        filename = path.replace(ya.settings.backup_dir + '/', '')
        file_timestamp = filename[:filename.index('-<')]
        if file_timestamp <= str(timestamp):
            break
    else:
        return []
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
