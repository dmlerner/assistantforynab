import ynabassistant as ya

_accounts = None  # by name
_category_groups = None  # by name
_categories = None  # by name
_payees = None  # by name
_transactions = None  # account_name: { transaction_id: transaction }


def _build_get_maps():
    global _accounts, _category_groups, _categories, _payees, _transactions

    _accounts and _accounts.clear()
    for a in ya.Assistant.accounts.values():
        assert a.name not in _accounts
        _accounts[a.name] = a

    _category_groups and _category_groups.clear()
    for cg in ya.Assistant.category_groups.values():
        assert cg.name not in _category_groups
        _category_groups[cg.name] = cg

    _categories and _categories.clear()
    for c in ya.Assistant.categories.values():
        assert c.name not in _categories
        _categories[c.name] = c

    _payees and _payees.clear()
    for p in ya.Assistant.payees.values():
        assert p.name not in _payees
        _payees[p.name] = p

    _transactions and _transactions.clear()
    __transactions = ya.utils.group_by(ya.Assistant.transactions, lambda t: t.account_name)
    for account_name in __transactions.values():
        _transactions[account_name] = ya.utils.by(__transactions[account_name], lambda t: t.id)


def get_account(name):
    return _accounts.get(name)


def get_category_group(name):
    return _category_groups.get(name)


def get_category(name):
    return _categories.get(name)


def get_payee(name):
    return _payees.get(name)


def get_transactions(account_name):
    return _transactions.get(account_name)
