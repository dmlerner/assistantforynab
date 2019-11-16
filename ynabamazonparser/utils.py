import collections
import datetime
import os
import sys

from ynabamazonparser import gui
from ynabamazonparser.config import settings


def equalish(a, b):
    return round(a, 4) == round(b, 4)


def get_log_path():
    log_name = str(settings.start_time) + '-log.txt'
    return os.path.join(settings.log_dir, log_name)


log_file = open(get_log_path(), 'a+')


def log(*x, verbosity=0, sep=' | ', end=os.linesep * 2):
    if verbosity >= settings.log_verbosity:
        print(datetime.datetime.now(), end=os.linesep, file=log_file)
        print(*x, sep=sep, end=end, file=log_file)
    if verbosity >= settings.print_verbosity:
        print(*x, sep=sep, end=end)


def quit():
    log('Quitting')
    if settings.close_browser_on_finish:
        gui.quit()
    log_file.close()
    sys.exit()


def group_by(collection, key):
    grouped = collections.defaultdict(list)
    for c in collection:
        grouped[key(c)].append(c)
    return grouped
