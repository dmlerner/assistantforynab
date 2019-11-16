from ynabamazonparser import amazon, ynab, utils, match
from ynabamazonparser.amazon import downloader, amazon


class Assistant:

    def load_amazon_data(self):
        utils.log('Loading Amazon')
        self.orders = downloader.load('orders')  # { order_id: order }
        self.items = downloader.load('items')  # { order_id: order }
        utils.log(utils.separator)

    def load_ynab_data(self):
        utils.log('Downloading YNAB')
        self.transactions = ynab.api_client.get_all_transactions()  # { (transaction)id: transaction }
        utils.log(utils.separator)

    def update_amazon_transactions(self):
        utils.log('Matching')
        potential_amazon_transactions = amazon.get_eligible_transactions(self.transactions)
        self.orders_by_transaction_id = match.match_all(potential_amazon_transactions, self.orders)
        for t_id, order in self.orders_by_transaction_id.items():
            t = self.transactions[t_id]
            items = self.items[order.order_id]
            assert items
            amazon.amazon.annotate(t, order, items)
            update_list = ynab.transactions_to_rest_update if len(items) == 1 else ynab.transactions_to_gui_update
            update_list.append(t)
        utils.log(utils.separator)
        ynab.update()
