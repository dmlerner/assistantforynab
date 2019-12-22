import ynab_api
import ynabassistant as ya
from ynabassistant import settings
import ynabassistant.backup
import ynabassistant.install
from ynabassistant.utils import utils


def init(should_clean=False):
    global configuration, api_client, accounts_api, categories_api, transactions_api, payees_api
    utils.log_info('api_client.init, shouldclean=', should_clean)
    configuration = ynab_api.configuration.Configuration()
    if should_clean or not settings.get('api_token'):
        ya.install.do(should_clean)
        assert settings.get('api_token')
    configuration.api_key['Authorization'] = settings.get('api_token')
    configuration.api_key_prefix['Authorization'] = 'Bearer'

    api_client = ynab_api.api_client.ApiClient(configuration)

    accounts_api = ynab_api.AccountsApi(api_client)
    categories_api = ynab_api.CategoriesApi(api_client)
    transactions_api = ynab_api.TransactionsApi(api_client)
    payees_api = ynab_api.PayeesApi(api_client)


init(True)


@ya.backup.local.save
def get_accounts():
    utils.log_debug('get_accounts')
    response = accounts_api.get_accounts(settings.budget_id)
    acs = response.data.accounts
    assert all(isinstance(ac, ynab_api.Account) for ac in acs)
    acs.sort(key=lambda ac: ac.name, reverse=True)
    return acs


@ya.backup.local.save
def get_transactions():
    utils.log_debug('get_transactions')
    response = transactions_api.get_transactions(settings.budget_id)
    ts = response.data.transactions
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
    ts.sort(key=lambda t: t.date, reverse=True)
    return ts


@utils.listy
@ya.backup.local.save
def update_transactions(transactions):
    utils.log_debug('update_transactions')
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in transactions)
    ut = utils.convert(transactions, ynab_api.UpdateTransaction)
    utw = ynab_api.UpdateTransactionsWrapper(transactions=ut)
    ts = transactions_api.update_transactions(settings.budget_id, utw).data.transactions
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
    return ts


@utils.listy
@ya.backup.local.save
def create_transactions(transactions):
    utils.log_debug('create_transactions')
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in transactions)
    st = utils.convert(transactions, ynab_api.SaveTransaction)
    stw = ynab_api.SaveTransactionsWrapper(transactions=st)
    ts = transactions_api.create_transaction(settings.budget_id, stw).data.transactions
    assert all(isinstance(t, ynab_api.TransactionDetail) for t in ts)
    return ts


@ya.backup.local.save
def get_category_groups():
    utils.log_debug('get_category_groups')
    response = categories_api.get_categories(settings.budget_id)
    groups = response.data.category_groups
    assert all(isinstance(g, ynab_api.CategoryGroupWithCategories) for g in groups)
    categories = [c for g in groups for c in g.categories]
    assert all(isinstance(c, ynab_api.Category) for c in categories)
    return groups


@utils.listy
@ya.backup.local.save
def update_categories(categories):
    utils.log_debug('update_categories', categories)
    assert all(isinstance(c, ynab_api.Category) for c in categories)
    assert all(isinstance(c.budgeted, int) for c in categories)
    updated_categories = []
    for c in categories:
        sc = utils.convert(c, ynab_api.SaveMonthCategory).pop()
        scw = ynab_api.SaveMonthCategoryWrapper(sc)
        utils.log_debug('c sc scw', c, sc, scw)
        updated = categories_api.update_month_category(settings.budget_id, "current", c.id, scw).data.category
        utils.log_debug('updated', updated)
        updated_categories.append(updated)
    updated_categories.sort(key=lambda c: c.name)
    return updated_categories


@ya.backup.local.save
def get_payees():
    utils.log_debug('get_payees')
    response = payees_api.get_payees(settings.budget_id)
    ps = response.data.payees
    assert all(isinstance(p, ynab_api.Payee) for p in ps)
    ps.sort(key=lambda p: p.name)
    return ps
