import ynabassistant as ya

_accounts = {}  # by name
_category_groups = {}  # by name
_categories = {}  # by name
_payees = {}  # by name
_transactions = {}  # account_name: { transaction_id: transaction }


def _build_get_maps():
    global _accounts, _category_groups, _categories, _payees, _transactions

    _accounts.clear()
    for a in ya.Assistant.accounts.values():
        if a.name in _accounts:
            ya.utils.log_debug('skipping; duplicate accounts with name %s: %s %s' % (a.name, _accounts[a.name], a))
            continue
        _accounts[a.name] = a

    _category_groups.clear()
    for cg in ya.Assistant.category_groups.values():
        if cg.name in _category_groups:
            ya.utils.log_debug('skipping; duplicate category_groups with name %s: %s %s' %
                               (cg.name, _category_groups[cg.name], a))
            continue
        _category_groups[cg.name] = cg

    _categories.clear()
    for c in ya.Assistant.categories.values():
        if c.name in _categories:
            ya.utils.log_debug('skipping; duplicate categories with name %s: %s %s' % (c.name, _categories[c.name], c))
            continue
        _categories[c.name] = c

    _payees.clear()
    for p in ya.Assistant.payees.values():
        # I have two payees with same name but different ID, somehow...
        # Njoy Tech, Sixth Avenue Aquarium
        # Which have 1 and 0 transactions, respectively
        # TODO: wtf
        if p.name in _payees:
            ya.utils.log_debug('skipping; duplicate payees with name %s: %s %s' % (p.name, _payees[p.name], p))
            continue
        _payees[p.name] = p

    _transactions = ya.utils.group_by(ya.Assistant.transactions.values(), lambda t: t.account_name)


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
