import datetime
import os
import sys
import pdb
import time

import settings
import amazon_downloader
import match
import ynab_api_client
import ynab_gui_client

from selenium.webdriver.chrome.options import Options
from selenium import webdriver  
#import httplib
import socket
from selenium.webdriver.remote.command import Command


def float_from_amazon_price(p):
    try:
        return float(p[1:])
    except:
        return None

def float_from_ynab_price(p):
    try:
        return abs(p/1000)
    except:
        return None

def equalish(a, b):
    try:
        return round(a, 4) == round(b, 4)
    except:
        return None

def get_log_name():
    return os.path.join(settings.log_path, str(settings.start_time) + '-log.txt')
log_file = open(get_log_name(), 'a+')

def log(*x, verbosity=0, sep=' | ', end=os.linesep*2):
    if verbosity >= settings.log_verbosity:
        print(datetime.datetime.now(), end=os.linesep, file=log_file)
        print(*x, sep=sep, end=end, file=log_file)
    if verbosity >= settings.print_verbosity:
        print(*x, sep=sep, end=end)

def datetime_from_amazon_date(d, fmt='%m/%d/%y'):
    return datetime.datetime.strptime(d, fmt)

def datetime_from_ynab_date(d, fmt='%Y-%m-%d'):
    return datetime.datetime.strptime(d, fmt)

_driver = None
def driver():
    global _driver
    ' TODO: make a selenium utils module with this and getters etc '
    if is_alive(_driver):
        return _driver
    options = Options()  
    options.add_argument("user-data-dir={}".format(settings.chrome_data_dir))
    options.add_argument("--disable-extensions")
    _driver = webdriver.Chrome(options=options)  
    return _driver

def is_alive(d):
    return d is not None
    '''
    try:
        d.execute(Command.STATUS)
        return True
    except (socket.error, httplib.CannotSendRequest):
        return False
    return False
    '''

def quit():
    log('Quitting')
    driver().quit()
    log_file.close()
    sys.exit()

