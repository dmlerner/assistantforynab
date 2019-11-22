import ynab_api

import ynabassistant as ya


class Client:
    def __init__(self):
        self.configuration = ynab_api.configuration.Configuration()
        self.configuration.api_key['Authorization'] = ya.settings.api_key
        self.configuration.api_key_prefix['Authorization'] = 'Bearer'

        self.api_client = ynab_api.api_client.ApiClient(self.configuration)
        self.accounts_api = ynab_api.AccountsApi(self.api_client)
        self.categories_api = ynab_api.CategoriesApi(self.api_client)
        self.transactions_api = ynab_api.TransactionsApi(self.api_client)

    def get_all_transactions(self):
        ya.utils.log_debug('get_all_transactions')
        response = self.transactions_api.get_transactions(ya.settings.budget_id)
        ya.utils.log_debug(response)
        ts = response.data.transactions
        assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
        ya.utils.log_info('Found %s transactions' % len(ts or []))
        ts.sort(key=lambda t: t.date, reverse=True)
        return ya.utils.by(response.data.transactions, lambda t: t.id)

    def update_transactions(self, transactions):  # TODO combine with create?
        ya.utils.log_debug('update_transactions', *transactions)
        assert all(isinstance(t, ynab_api.TransactionDetail) for t in transactions)
        ut = ya.utils.convert(transactions, ynab_api.UpdateTransaction)
        utw = ynab_api.UpdateTransactionsWrapper(transactions=ut)
        response = self.transactions_api.update_transactions(ya.settings.budget_id, utw)
        ya.utils.log_debug(response)

    def create_transactions(self, transactions):
        ya.utils.log_debug('create_transactions', *transactions)
        assert all(isinstance(t, ynab_api.TransactionDetail) for t in transactions)
        st = ya.utils.convert(transactions, ynab_api.SaveTransaction)
        stw = ynab_api.SaveTransactionsWrapper(transactions=st)
        response = self.transactions_api.create_transaction(ya.settings.budget_id, stw)
        ya.utils.log_debug(response)


    def get_categories(self):
        ya.utils.log_debug('get_categories')
        response = self.categories_api.get_categories(ya.settings.budget_id)
        ya.utils.log_debug(response)
        groups = response.data.category_groups
        assert all(isinstance(g, ynab_api.CategoryGroupWithCategories) for g in groups)
        categories = [c for g in groups for c in g.categories]
        assert all(isinstance(c, ynab_api.Category) for c in categories)
        return ya.utils.by(categories, lambda c: c.id)
