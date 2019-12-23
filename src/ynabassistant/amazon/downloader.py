import os
import datetime
import time
import glob
import csv
import sys
import traceback

import ynabassistant as ya
from ynabassistant.utils import utils, gui
from ynabassistant import settings

from . import Item, Order


def get_downloaded_csv_filenames():
    utils.log_debug('get_downloaded_csv_filenames')
    return set(
        glob.glob(os.path.join(ya.settings.downloads_dir, '*.csv')))


def wait_for_download(timeout=30):
    utils.log_debug('wait_for_download')
    filenames_before = get_downloaded_csv_filenames()
    for i in range(timeout):
        filenames = get_downloaded_csv_filenames()
        new_filenames = filenames - filenames_before
        if new_filenames:
            assert len(new_filenames) == 1
            break
        time.sleep(1)
    return new_filenames.pop()


def parse_items(item_dicts):
    utils.log_debug('parse_items', len(item_dicts))
    return utils.group_by(map(Item, item_dicts), lambda i: i.id)  # this is an Order.id


def parse_orders(order_dicts):
    utils.log_debug('parse_orders', len(order_dicts))
    orders = map(Order, order_dicts)
    return combine_orders(orders)


data_parsers = {'items': parse_items, 'orders': parse_orders}
' TODO: get refunds, returns '
csv_paths = {k: os.path.join(ya.settings.data_dir, k + '.csv')
             for k in data_parsers}


def read(p):
    with open(p, newline='\n') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        return list(reader)


@utils.listy
def combine_orders(orders):
    utils.log_debug('combine_orders')
    combined = {}
    for order in orders:
        if order.id in combined:
            combined[order.id] += order  # overloaded operator
        else:
            combined[order.id] = order
    return combined


def stale(path):
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.datetime.now() - mtime > settings.max_amazon_staleness_days * utils.one_day


def enter_start_date():
    today = datetime.datetime.now()
    start_date = today - utils.one_day * settings.max_amazon_eligible_days
    month, day, year = start_date.strftime('%B %d %Y').split()
    d = gui.driver()
    d.find_element_by_id('report-month-start').click()
    d.find_element_by_id('report-month-start').send_keys(month)
    d.find_element_by_id('report-day-start').click()
    d.find_element_by_id('report-day-start').send_keys(day)
    d.find_element_by_id('report-year-start').click()
    d.find_element_by_id('report-year-start').send_keys(year)


def load(data_type):
    utils.log_debug('load', data_type)
    assert data_type in data_parsers
    target_path = csv_paths[data_type]
    try:
        if not os.path.exists(target_path) or stale(target_path):
            d = gui.driver()
            url = 'https://smile.amazon.com/gp/b2b/reports'
            if url not in d.current_url:
                d.get(url)

            d.find_element_by_id('report-use-today').click()
            enter_start_date()
            d.find_element_by_id('report-type').click()
            d.find_element_by_id('report-type').send_keys(data_type)
            d.find_element_by_id('report-confirm').click()
            path = wait_for_download()
            utils.log_debug(path, target_path)
            os.rename(path, target_path)

    except BaseException:
        utils.log_exception_debug()
        if 'AttributeError' in traceback.format_exc():  # TODO: only retry on missing csv
            utils.log_info('real error', traceback.format_exc())
            sys.exit()
        if input('One more try? [Y/n]').lower() != 'n':
            load(data_type)

    list_of_dicts = read(target_path)
    utils.log_info('Found %s %s' % (len(list_of_dicts), data_type))
    return data_parsers[data_type](list_of_dicts)
