import datetime
import os
import sys
import pdb
import time

import utils
import amazon_downloader
import match
import ynab_api_client
import ynab_gui_client

utils.log('Loading amazon data')
amazon_data = amazon_downloader.load_all()
utils.log('Downloading transactions from your ynab')
transactions = ynab_api_client.get_transactions_to_update()
utils.log('Matching the amazon data to the transactions')
pdb.set_trace()
orders_by_transaction_id = match.match_all(transactions, amazon_data['orders'])
utils.log('Putting the order ids as ynab memo lines so we can find them in the gui')
ynab_api_client.update_all(transactions, orders_by_transaction_id)
utils.log('Entering all the information in the gui via Selenium/Chrome')
ynab_gui_client.enter_all_transactions(transactions, orders_by_transaction_id)
utils.quit()
