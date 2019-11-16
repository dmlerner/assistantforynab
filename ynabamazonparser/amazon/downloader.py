import traceback
import pdb
import os
import time

from ynabamazonparser import utils, gui
from ynabamazonparser.config import settings
from ynabamazonparser.amazon.item import Item
from ynabamazonparser.amazon.order import Order

import glob
import csv
import collections


def get_downloaded_csv_filenames():
    return set(
        glob.glob(os.path.join(settings.downloads_dir, '*.csv')))


def wait_for_download(timeout=30):
    filenames_before = get_downloaded_csv_filenames()
    for i in range(timeout):
        filenames = get_downloaded_csv_filenames()
        new_filenames = filenames - filenames_before
        if new_filenames:
            assert len(new_filenames) == 1
            break
        time.sleep(1)
    return new_filenames.pop()


' TODO: get refunds, returns '
data_types = 'items', 'orders'
csv_paths = {k: os.path.join(settings.data_dir, k + '.csv')
             for k in data_types}
constructors = {'items': Item, 'orders': Order}
data = {}


def missing_csv(data_type):
    return not os.path.exists(csv_paths[data_type])


def read(p):
    with open(p, newline='\n') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        return list(reader)


def parse(d, data_type):
    return constructors[data_type].from_dict(d)


def combine_orders():
    combined = {}
    for order in data['orders']:
        if order.order_id in combined:
            combined[order.order_id] += order
        else:
            combined[order.order_id] = order
    data['orders'] = list(combined.values())
    utils.log('Found %s unique orders' % len(data['orders']))


def load(data_type):
    target_path = csv_paths[data_type]
    try:
        if settings.force_download_amazon or missing_csv(data_type):
            d = gui.driver()
            url = 'https://smile.amazon.com/gp/b2b/reports'
            if d.current_url != url:
                d.get(url)

            d.find_element_by_id('report-last30Days').click()
            d.find_element_by_id('report-type').click()
            d.find_element_by_id('report-type').send_keys(data_type)
            d.find_element_by_id('report-confirm').click()
            path = wait_for_download()
            os.rename(path, target_path)

        list_of_dicts = read(target_path)
        data[data_type] = [parse(d, data_type) for d in list_of_dicts]
        utils.log('Found %s %s' % (len(data[data_type]), data_type))
        return data[data_type]
    except BaseException:
        utils.log('Probably this failed because you need to log in...')
        utils.log('Type q then enter to quit, or anything else to try again.')
        if input('One more try?').lower() != 'q':
            load(data_type)
        else:
            utils.log(traceback.format_exc())
            utils.quit()


def load_all():
    for t in data_types:
        load(t)
    combine_orders()
    return data


def get_items_by_order_id():
    load('items')  # I should not have to reload...
    items = data['items']
    assert items
    items_by_order_id = collections.defaultdict(list)
    for item in items:
        items_by_order_id[item.order_id].append(item)
    return items_by_order_id


'''
order total may not equal sum of item costs
because order consider coupons and probably also shipping
but order does have shipping cost field
and promotions field
not clear that I can get per-item promotion breakdowns

orders may have an order id repeated, splitting the cost across them
'''
