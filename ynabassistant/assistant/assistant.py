import ynabassistant as ya


class Assistant:

    def load_amazon_data(self):
        ya.utils.log_info('Loading Amazon')
        self.orders = ya.amazon.downloader.load('orders')
        self.items_by_order_id = ya.amazon.downloader.load('items')
        ya.utils.log_info(ya.utils.separator)

    def load_ynab_data(self):
        ya.utils.log_info('Downloading YNAB')
        self.transactions = ya.ynab.api_client.get_all_transactions()
        self.categories = ya.ynab.api_client.get_categories()
        ya.utils.log_info(ya.utils.separator)

    def update_amazon_transactions(self):
        ya.utils.log_info('Matching Amazon orders to YNAB transactions')
        potential_amazon_transactions = ya.amazon.get_eligible_transactions(self.transactions)
        orders_by_transaction_id = ya.amazon.match.match_all(potential_amazon_transactions, self.orders)
        for t in self.transactions:
            if t.id in orders_by_transaction_id:
                order = orders_by_transaction_id[t.id]
                items = self.items_by_order_id[order.order_id]
                assert items
                ya.amazon.annotate(t, order, items)
                update_list = ya.ynab.transactions_to_rest_update if len(items) == 1 \
                    else ya.ynab.transactions_to_gui_update
                update_list.append(t)
        ya.utils.log_info(ya.utils.separator)

    def update_ynab(self):
        ya.ynab.update()
