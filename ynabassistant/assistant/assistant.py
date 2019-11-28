import ynabassistant as ya


class Assistant:

    @staticmethod
    def load_amazon_data():
        ya.utils.log_info('Loading Amazon')
        Assistant.orders = ya.utils.by(ya.amazon.downloader.load('orders'), lambda o: o.order_id)
        Assistant.items = ya.amazon.downloader.load('items')
        ya.utils.log_info(ya.utils.separator)

    @staticmethod
    def download_ynab(accounts=False, transactions=False, category_groups=False, categories=False, payees=False):
        ya.utils.log_info('Downloading YNAB')
        assert accounts or transactions or category_groups or category_groups or payees
        if accounts:
            Assistant.accounts = ya.utils.by(ya.ynab.api_client.get_all_accounts(), lambda ac: ac.id)
        if transactions:
            Assistant.transactions = ya.utils.by(ya.ynab.api_client.get_all_transactions(), lambda t: t.id)
        if category_groups or categories:
            Assistant.category_groups = ya.utils.by(ya.ynab.api_client.get_category_groups(), lambda g: g.id)
        if categories:
            Assistant.categories = ya.utils.by((c for g in Assistant.category_groups.values()
                                                for c in g.categories), lambda c: c.id)
        if payees:
            Assistant.payees = ya.utils.by(ya.ynab.api_client.get_payees(), lambda p: p.id)
        ya.assistant.utils._build_get_maps()
        ya.utils.log_info(ya.utils.separator)

    @staticmethod
    def download_all_ynab():
        Assistant.download_ynab(True, True, True, True, True)

    @staticmethod
    def update_amazon_transactions():
        ya.utils.log_info('Matching Amazon orders to YNAB transactions')
        potential_amazon_transactions = ya.amazon.get_eligible_transactions(Assistant.transactions)
        orders_by_transaction_id = ya.amazon.match.match_all(potential_amazon_transactions, Assistant.orders)
        for t_id, order in orders_by_transaction_id.items():
            order = orders_by_transaction_id[t_id]
            i = Assistant.items[order.order_id]
            assert i
            t = Assistant.transactions[t_id]
            ya.amazon.annotate(t, order, i)
            ya.ynab.queue_update(t, Assistant.payees, Assistant.categories)
        ya.utils.log_info(ya.utils.separator)

    @staticmethod
    def update_ynab():
        ya.ynab.do()
