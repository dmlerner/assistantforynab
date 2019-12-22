import os
import time
import glob
import csv

import utils
import settings

from . import Item, Order


def get_downloaded_csv_filenames():
    utils.log_debug('get_downloaded_csv_filenames')
    return set(
        glob.glob(os.path.join(settings.downloads_dir, '*.csv')))


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
csv_paths = {k: os.path.join(settings.data_dir, k + '.csv')
             for k in data_parsers}


def missing_csv(data_type):
    return not os.path.exists(csv_paths[data_type])


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


def load(data_type):
    utils.log_debug('load', data_type)
    assert data_type in data_parsers
    target_path = csv_paths[data_type]
    try:
        if settings.force_download_amazon or missing_csv(data_type):
            d = utils.gui.driver()
            url = 'https://smile.amazon.com/gp/b2b/reports'
            if url not in d.current_url:
                d.get(url)

            d.find_element_by_id('report-last30Days').click()
            d.find_element_by_id('report-type').click()
            d.find_element_by_id('report-type').send_keys(data_type)
            d.find_element_by_id('report-confirm').click()
            path = wait_for_download()
            utils.log_debug(path, target_path)
            os.rename(path, target_path)

    except BaseException:
        utils.log_exception_debug()
        if input('One more try? [Y/n]').lower() != 'n':
            load(data_type)

    list_of_dicts = read(target_path)
    utils.log_info('Found %s %s' % (len(list_of_dicts), data_type))
    return data_parsers[data_type](list_of_dicts)
