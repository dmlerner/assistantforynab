import ynabassistant as ya


class Assistant:

    @staticmethod
    def load_amazon_data():
        ya.utils.log_info('Loading Amazon')
        Assistant.orders = ya.utils.by(ya.amazon.downloader.load('orders'), lambda o: o.order_id)
        Assistant.items = ya.amazon.downloader.load('items')
        ya.utils.log_info(ya.utils.separator)

    @staticmethod
    def download_ynab(accounts=False, transactions=False, categories=False, payees=False):
        ya.utils.log_info('Downloading YNAB')
        assert accounts or transactions or categories or payees
        Assistant.accounts = accounts and ya.utils.by(ya.ynab.api_client.get_all_accounts(), lambda ac: ac.id) or {}
        Assistant.transactions = transactions and ya.utils.by(
            ya.ynab.api_client.get_all_transactions(), lambda t: t.id) or {}
        Assistant.category_groups = categories and ya.utils.by(
            ya.ynab.api_client.get_category_groups(), lambda g: g.id) or {}
        Assistant.categories = categories and ya.utils.by(
            (c for g in Assistant.category_groups.values() for c in g.categories), lambda c: c.id) or {}
        Assistant.payees = payees and ya.utils.by(ya.ynab.api_client.get_payees(), lambda p: p.id) or {}
        ya.assistant.utils._build_get_maps(accounts, transactions, categories, payees)
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
