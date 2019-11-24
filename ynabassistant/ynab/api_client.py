import ynab_api

import ynabassistant as ya
from . import utils


configuration = ynab_api.configuration.Configuration()
configuration.api_key['Authorization'] = ya.settings.api_key
configuration.api_key_prefix['Authorization'] = 'Bearer'

api_client = ynab_api.api_client.ApiClient(configuration)

accounts_api = ynab_api.AccountsApi(api_client)
categories_api = ynab_api.CategoriesApi(api_client)
transactions_api = ynab_api.TransactionsApi(api_client)
payees_api = ynab_api.PayeesApi(api_client)


@utils.save_and_log
def get_all_accounts():
    response = accounts_api.get_accounts(ya.settings.budget_id)
    acs = response.data.accounts
    assert all(isinstance(ac, ynab_api.Account) for ac in acs)
    ya.utils.log_info('Found %s accounts' % len(acs or []))
    acs.sort(key=lambda ac: ac.name, reverse=True)
    return acs


@utils.save_and_log
def get_all_transactions():
    response = transactions_api.get_transactions(ya.settings.budget_id)
    ts = response.data.transactions
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
    ya.utils.log_info('Found %s transactions' % len(ts or []))
    ts.sort(key=lambda t: t.date, reverse=True)
    return ts


@utils.save_and_log
def update_transactions(transactions):
    if not transactions:
        return
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in transactions)
    ut = ya.utils.convert(transactions, ynab_api.UpdateTransaction)
    utw = ynab_api.UpdateTransactionsWrapper(transactions=ut)
    ts = transactions_api.update_transactions(ya.settings.budget_id, utw).data.transactions
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
    return ts


@utils.save_and_log
def create_transactions(transactions):
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in transactions)
    st = ya.utils.convert(transactions, ynab_api.SaveTransaction)
    stw = ynab_api.SaveTransactionsWrapper(transactions=st)
    ts = transactions_api.create_transaction(ya.settings.budget_id, stw).data.transactions
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
    return ts


@utils.save_and_log
def get_category_groups():
    response = categories_api.get_categories(ya.settings.budget_id)
    groups = response.data.category_groups
    ya.utils.log_info('Found %s category groups' % len(groups or []))
    assert all(isinstance(g, ynab_api.CategoryGroupWithCategories) for g in groups)
    categories = [c for g in groups for c in g.categories]
    assert all(isinstance(c, ynab_api.Category) for c in categories)
    ya.utils.log_info('Found %s categories' % len(categories or []))
    return groups


@utils.save_and_log
def update_categories(categories):
    if not categories:
        return
    assert all(isinstance(c, ynab_api.Category) for c in categories)
    updated_categories = []
    for c in categories:
        sc = ya.utils.convert(c, ynab_api.SaveMonthCategory)
        scw = ynab_api.SaveMonthCategoryWrapper(sc)
        updated_categories.append(categories_api.update_month_category(
            ya.settings.budget_id, "current", c.id, scw).data.category)
    updated_categories.sort(lambda c: c.name)
    return updated_categories


@utils.save_and_log
def get_payees():
    response = payees_api.get_payees(ya.settings.budget_id)
    ps = response.data.payees
    assert all(isinstance(p, ynab_api.Payee) for p in ps)
    ya.utils.log_info('Found %s payees' % len(ps or []))
    ps.sort(key=lambda p: p.name)
    return ps
