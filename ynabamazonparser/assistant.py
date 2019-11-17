import ynabamazonparser as yap


class Assistant:

    def load_amazon_data(self):
        yap.utils.log('Loading Amazon')
        self.orders = yap.amazon.downloader.load('orders')  # { order_id: order }
        self.items = yap.amazon.downloader.load('items')  # { order_id: [item] }
        yap.utils.log(yap.utils.separator)

    def load_ynab_data(self):
        yap.utils.log('Downloading YNAB')
        self.transactions = yap.ynab.api_client.get_all_transactions()  # { (transaction)id: transaction }
        yap.utils.log(yap.utils.separator)

    def update_amazon_transactions(self):
        yap.utils.log('Matching')
        potential_amazon_transactions = yap.amazon.amazon.get_eligible_transactions(self.transactions)
        yap.utils.log('potential', potential_amazon_transactions)
        self.orders_by_transaction_id = yap.match.match_all(potential_amazon_transactions, self.orders)
        for t_id, order in self.orders_by_transaction_id.items():
            t = self.transactions[t_id]
            items = self.items[order.order_id]
            assert items
            yap.utils.log('before amazon annotate t=', t)
            yap.utils.log('before amazon annotate order=', order)
            yap.utils.log('before amazon annotate items=', items)
            yap.amazon.amazon.annotate(t, order, items)
            yap.utils.log('after amazon annotate t=', t)
            yap.utils.log('after amazon annotate order=', order)
            yap.utils.log('after amazon annotate items=', items)
            update_list = yap.ynab.ynab.transactions_to_rest_update if len(items) == 1 \
                else yap.ynab.ynab.transactions_to_gui_update
            update_list.append(t)
        yap.utils.log(yap.utils.separator)

    def update_ynab(self):
        yap.ynab.ynab.update()
