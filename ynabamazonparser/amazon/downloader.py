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
    utils.log('get_downloaded_csv_filenames', [(k, len(data[k])) for k in data])
    return set(
    glob.glob(os.path.join(settings.downloads_path, '*.csv')))


def wait_for_download(timeout=30):
    utils.log('wait_for_download', [(k, len(data[k])) for k in data])
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
csv_paths = {k: os.path.join(settings.data_path, k + '.csv')
             for k in data_types}
constructors = {'items': Item, 'orders': Order}
data = {}


def missing_csv(data_type):
    utils.log('missing_csv', [(k, len(data[k])) for k in data])
    return not os.path.exists(csv_paths[data_type])


def read(p):
    utils.log('read', [(k, len(data[k])) for k in data])
    with open(p, newline='\n') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        return list(reader)


def parse(d, data_type):
    utils.log('parse', [(k, len(data[k])) for k in data])
    return constructors[data_type].from_dict(d)


def load(data_type):
    utils.log('load', [(k, len(data[k])) for k in data])
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
    except:
        utils.log('Probably this failed because you need to log in...')
        utils.log('Type q then enter to quit, or anything else to try again.')
        if input('One more try?').lower() != 'q':
            load(data_type)
        else:
            utils.log(traceback.format_exc())
            utils.quit()


def load_all():
    utils.log('load_all', [(k, len(data[k])) for k in data])
    for t in data_types:
        load(t)
    return data


def get_items_by_order_id():
    utils.log('get_items_by_order_id', [(k, len(data[k])) for k in data])
    load('items')# I should not have to reload...
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
