import ynabassistant as ya
import collections


class Assistant:

    accounts = ya.utils.Cache()
    transactions = ya.utils.TransactionCache(accounts)
    categories = ya.utils.Cache()
    category_groups = ya.utils.Cache()
    payees = ya.utils.Cache()

    orders = collections.defaultdict(list)
    items = {}

    def load_amazon_data():
        ya.utils.log_info('Loading Amazon')
        Assistant.orders = ya.amazon.downloader.load('orders')  # by order.id
        Assistant.items = ya.amazon.downloader.load('items')  # grouped by order.id
        ya.utils.log_info(ya.utils.separator)

    def load_ynab(accounts=False, transactions=False, categories=False, payees=False, local=False):
        assert accounts or transactions or categories or payees
        source = ya.backup.local if local else ya.ynab.api_client

        # Need accounts to validate transactions pending deleted account bug fix
        if transactions or accounts:
            Assistant.accounts.store(source.get_accounts())
            if accounts:
                ya.utils.log_info('Found %s accounts' % len(Assistant.accounts))

        if transactions:
            Assistant.transactions.store(source.get_transactions())
            ya.utils.log_info('Found %s transactions' % len(Assistant.transactions))

        if categories:
            Assistant.category_groups.store(source.get_category_groups())
            ya.utils.log_info('Found %s category groups' % len(Assistant.category_groups))
            Assistant.categories.store(c for g in Assistant.category_groups for c in g.categories)
            ya.utils.log_info('Found %s categories' % len(Assistant.categories))

        if payees:
            Assistant.payees.store(source.get_payees())
            ya.utils.log_info('Found %s payees' % len(Assistant.payees))

        ya.utils.log_info(ya.utils.separator)

    def download_ynab(accounts=False, transactions=False, categories=False, payees=False):
        ya.utils.log_info('Downloading YNAB')
        Assistant.load_ynab(accounts, transactions, categories, payees, local=False)

    def restore_ynab(accounts=False, transactions=False, categories=False, payees=False):
        ya.utils.log_info('Restoring YNAB')
        Assistant.load_ynab(accounts, transactions, categories, payees, local=True)

    def download_all_ynab():
        Assistant.download_ynab(True, True, True, True)

    def restore_all_ynab():
        Assistant.restore_ynab(True, True, True, True)

    def update_amazon_transactions():
        ya.utils.log_info('Matching Amazon orders to YNAB transactions')
        potential_amazon_transactions = ya.amazon.get_eligible_transactions(Assistant.transactions)
        orders_by_transaction_id = ya.amazon.match.match_all(potential_amazon_transactions, Assistant.orders)
        for t_id, order in orders_by_transaction_id.items():
            order = orders_by_transaction_id[t_id]
            i = Assistant.items[order.id]
            assert i
            t = Assistant.transactions.get(t_id)
            ya.amazon.annotate(t, order, i)
            # ya.ynab.queue_update(t, Assistant.payees, Assistant.categories)
            ya.ynab.queue_update(t)
        ya.utils.log_info(ya.utils.separator)

    def update_ynab():
        ya.ynab.do()
