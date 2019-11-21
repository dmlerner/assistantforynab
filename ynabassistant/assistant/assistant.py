import ynabassistant as ya


class Assistant:

    def load_amazon_data(self):
        ya.utils.log_info('Loading Amazon')
        self.orders = ya.amazon.downloader.load('orders')  # { order_id: order }
        self.items = ya.amazon.downloader.load('items')  # { order_id: [item] }
        ya.utils.log_info(ya.utils.separator)

    def load_ynab_data(self):
        ya.utils.log_info('Downloading YNAB')
        self.transactions = ya.ynab.api_client.get_all_transactions()  # { (transaction)id: transaction }
        self.categories = ya.ynab.api_client.get_categories()  # { category_id: category }
        ya.utils.log_info(ya.utils.separator)

    def update_amazon_transactions(self):
        ya.utils.log_info('Matching Amazon orders to YNAB transactions')
        potential_amazon_transactions = ya.amazon.amazon.get_eligible_transactions(self.transactions)
        self.orders_by_transaction_id = ya.amazon.match.match_all(potential_amazon_transactions, self.orders)
        for t_id, order in self.orders_by_transaction_id.items():
            t = self.transactions[t_id]
            items = self.items[order.order_id]
            assert items
            ya.amazon.amazon.annotate(t, order, items)
            update_list = ya.ynab.ynab.transactions_to_rest_update if len(items) == 1 \
                else ya.ynab.ynab.transactions_to_gui_update
            update_list.append(t)
        ya.utils.log_info(ya.utils.separator)

    def update_ynab(self):
        ya.ynab.ynab.update()
