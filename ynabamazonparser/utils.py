from ynabamazonparser import settings, selenium
import datetime
import pdb
import os
import sys


def equalish(a, b):
    return round(a, 4) == round(b, 4)


def get_log_path():
    pdb.set_trace()
    log_name = str(settings.start_time) + '-log.txt'
    return os.path.join(settings.log_path, log_name)


log_file = open(get_log_path(), 'a+')


def log(*x, verbosity=0, sep=' | ', end=os.linesep*2):
    if verbosity >= settings.log_verbosity:
        print(datetime.datetime.now(), end=os.linesep, file=log_file)
        print(*x, sep=sep, end=end, file=log_file)
    if verbosity >= settings.print_verbosity:
        print(*x, sep=sep, end=end)


def quit():
    log('Quitting')
    if settings.close_browser_on_finish:
        selenium.quit()
    log_file.close()
    sys.exit()