import ynab_api

import ynabassistant as ya

configuration = ynab_api.configuration.Configuration()
configuration.api_key['Authorization'] = ya.settings.api_key
configuration.api_key_prefix['Authorization'] = 'Bearer'

api_client = ynab_api.api_client.ApiClient(configuration)
accounts_api = ynab_api.AccountsApi(api_client)
categories_api = ynab_api.CategoriesApi(api_client)
transactions_api = ynab_api.TransactionsApi(api_client)

def get_all_transactions():
    ya.utils.log_debug('get_all_transactions')
    response = transactions_api.get_transactions(ya.settings.budget_id)
    ya.utils.log_debug(response)
    ts = response.data.transactions
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
    ya.utils.log_info('Found %s transactions' % len(ts or []))
    ts.sort(key=lambda t: t.date, reverse=True)
    return ts

def update_transactions(transactions):
    ya.utils.log_debug('update_transactions', *transactions)
    if not transactions:
        return
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in transactions)
    ut = ya.utils.convert(transactions, ynab_api.UpdateTransaction)
    utw = ynab_api.UpdateTransactionsWrapper(transactions=ut)
    response = transactions_api.update_transactions(ya.settings.budget_id, utw)
    ya.utils.log_debug(response)

def create_transactions(transactions):
    ya.utils.log_debug('create_transactions', *transactions)
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in transactions)
    st = ya.utils.convert(transactions, ynab_api.SaveTransaction)
    stw = ynab_api.SaveTransactionsWrapper(transactions=st)
    response = transactions_api.create_transaction(ya.settings.budget_id, stw)
    ya.utils.log_debug(response)


def get_categories():
    ya.utils.log_debug('get_categories')
    response = categories_api.get_categories(ya.settings.budget_id)
    ya.utils.log_debug(response)
    groups = response.data.category_groups
    assert all(isinstance(g, ynab_api.CategoryGroupWithCategories) for g in groups)
    categories = [c for g in groups for c in g.categories]
    assert all(isinstance(c, ynab_api.Category) for c in categories)
    return categories
