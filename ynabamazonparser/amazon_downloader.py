import datetime
import os
import sys
import pdb
import time

import settings
import utils
import match
import ynab_api_client
import ynab_gui_client

import glob
import csv
import collections

get_downloaded_csv_filenames = lambda: set(glob.glob(os.path.join(settings.downloads_path, '*.csv')))

def wait_for_download(timeout=30):
    filenames_before = get_downloaded_csv_filenames()
    for i in range(timeout):
        filenames = get_downloaded_csv_filenames()
        new_filenames = filenames - filenames_before
        if len(new_filenames) == 1:
            filename_orders = filenames.pop()
            break
        if len(new_filenames) > 1:
            'TODO'
            utils.log('Somehow multiple csv files downloaded while I was waiting', 'Picking randomly')
            break
        time.sleep(1)
    return new_filenames.pop()

    generated_filename = new_filenames.pop()
    if name:
        path = downloads_path + name
        if not os.path.exists(name):
            os.rename(generated_filename, path)
            return path
    return generated_filename

' TODO: get refunds, returns '
data_types = 'items', 'orders'
csv_paths = { k: os.path.join(settings.data_path, k + '.csv') for k in data_types }
data = {}

def missing_csv(data_type):
    return not os.path.exists(csv_paths[data_type])

def parse(p):
    with open(p, newline='\n') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        return  list(reader)

def load(data_type):
    target_path = csv_paths[data_type]
    try:
        if settings.force_download_amazon or missing_csv(data_type):
            d = utils.driver()
            url = 'https://smile.amazon.com/gp/b2b/reports'
            if d.current_url != url:
                d.get(url)  

            d.find_element_by_id('report-last30Days').click()
            d.find_element_by_id('report-type').click()
            d.find_element_by_id('report-type').send_keys(data_type)
            d.find_element_by_id('report-confirm').click()
            path = wait_for_download()
            os.rename(path, target_path)

        data[data_type] = parse(target_path)
        return data[data_type]
    except:
        utils.log('Probably this failed because you need to log in...')
        utils.log('Type q then enter to quit, or anything else to try again.')
        if input('One more try?').lower() != 'q':
            load(data_type)
        else:
            utils.quit()


def load_all():
    for t in data_types:
        load(t)
    return data

def get_items_by_order_id(items=None):
    if items is None:
        items = data['items']
    assert items
    items_by_order_id = collections.defaultdict(list)
    for item in items:
        items_by_order_id[item['Order ID']].append(item)
    return items_by_order_id

'''
order total may not equal sum of item costs
because order consider coupons and probably also shipping
but order does have shipping cost field
and promotions field
not clear that I can get per-item promotion breakdowns

orders may have an order id repeated, splitting the cost across them
'''
