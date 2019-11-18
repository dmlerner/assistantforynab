import collections
import glob
import datetime
import os
import sys
import pdb

import ynabamazonparser as yap


def get_log_path():
    log_name = str(yap.settings.start_time) + '-log.txt'
    return os.path.join(yap.settings.log_dir, log_name)


log_file = open(get_log_path(), 'a+')


def log_info(*x, sep=os.linesep, end=os.linesep * 2):
    _log(*x, verbosity=yap.settings.info_verbosity, sep=sep, end=end)


def log_debug(*x, sep=os.linesep, end=os.linesep * 2):
    _log(*x, verbosity=yap.settings.debug_verbosity, sep=sep, end=end)


def log_error(*x, sep=os.linesep, end=os.linesep * 2):
    _log(*x, verbosity=yap.settings.error_verbosity, sep=sep, end=end)


def _log(*x, verbosity=0, sep=' | ', end=os.linesep * 2):
    if verbosity <= yap.settings.log_verbosity:
        print(datetime.datetime.now(), end=os.linesep, file=log_file)
        print(*x, sep=sep, end=end, file=log_file)
    if verbosity <= yap.settings.print_verbosity:
        print(*x, sep=sep, end=end)


def newer_than(d, days_ago=30):
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days_ago)
    return d > cutoff


def clear_old_logs():
    log_debug('clear_old_logs')
    for name in glob.glob(yap.settings.log_dir):
        path = os.path.join(yap.settings.log_dir, name)
        modified_time  = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        if not newer_than(modified_time, yap.settings.max_log_age_days):
            os.remove(path)


clear_old_logs()


def quit(gui_quit=False):
    log_info('Quitting')
    if gui_quit or yap.settings.close_browser_on_finish:
        yap.gui.quit()
    log_file.close()
    sys.exit()


def group_by(collection, key):
    grouped = collections.defaultdict(list)
    for c in collection:
        grouped[key(c)].append(c)
    return grouped


def by(collection, key):
    d = collections.OrderedDict()
    for c in collection:
        d[key(c)] = c
    return d


separator = '\n' + '.' * 100 + '\n'


def equalish(a, b):
    return round(a, 4) == round(b, 4)


def debug():
    pdb.set_trace()
