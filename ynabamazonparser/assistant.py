from ynabamazonparser import amazon, ynab, utils, match
from ynabamazonparser.config import settings


separator = '\n' + '.' * 100 + '\n'


class Assistant:
    def load_amazon_data(self):
        utils.log('Loading Amazon')
        self.orders = amazon.downloader.load('orders')
        self.items = amazon.downloader.load('items')
        utils.log(separator)

    def load_ynab_data(self):
        utils.log('Downloading YNAB')
        self.transactions = ynab.api_client.get_transactions_to_update()
        utils.log(separator)

    def match_amazon(self):
        utils.log('Matching')
        self.orders_by_transaction_id, self.items_by_order_id = \
            match.match_all(self.transactions, self.orders, self.items)
        if not orders_by_transaction_id:
            utils.log('No matching orders')
        utils.log(separator)

    def data(self):
        return self.transactions, self.orders, self.items

    def update_ynab():
        ynab.ynab.
        ynab.api_client.update_all(nonsplits)
        ynab.api_client.annotate_split_transactions

    utils.log('Putting order ids as ynab memo to can find them in the gui')
    api_client.update_all(transactions)
    utils.log(separator)

    utils.log('Entering all the information in the gui via Selenium/Chrome')
    gui_client.enter_all_transactions(
        transactions, orders_by_transaction_id, items_by_order_id)
    utils.log(separator)

    utils.quit()
