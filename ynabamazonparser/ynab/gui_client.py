import traceback

import ynabamazonparser as yap


def load_gui():
    url = 'https://app.youneedabudget.com/%s/accounts' % yap.settings.budget_id
    d = yap.gui.driver()
    d.get(url)
    if not yap.gui.get('user-logged-in'):
        selection = input(
            'please log in then press any key to continue, or q to quit').lower()
        if selection == 'q':
            yap.utils.quit()
        load_gui()


def enter_fields(fields, values):
    ' TODO: could this be simpler? is that last tab actually a problem? '
    for i, (f, v) in enumerate(zip(fields, values)):
        f.clear()
        f.send_keys(str(v))
        if i != len(fields) - 1:
            f.send_keys(yap.gui.Keys.TAB)


def get_category(transaction):
    if not transaction.category_name or 'Split (Multiple' in transaction.category_name:
        yap.utils.log('Warning: invalid category %s' % transaction.category_name)
        ' ynab would fail to download with ynab_api_client if `transaction` is a split transaction '
        ' even though you can hit save in the ui '
        ' hence using a default '
        assert yap.settings.default_category
        yap.utils.log('Using default: %s' % yap.settings.default_category)
        return yap.settings.default_category
    return transaction.category_name


def enter_item(transaction, payee_element, category_element, memo_element, outflow_element):
    'TODO/BUG: "Return: Amazon" category is equivalent to "AnythingElse: Amazon"'
    # TODO rename
    category = get_category(transaction)
    enter_fields((payee_element, category_element, memo_element, outflow_element),
                 (transaction.payee_name, category, transaction.memo, transaction.amount))


def locate_transaction(t):
    search = yap.gui.get('transaction-search-input')
    search.clear()
    search.send_keys('Memo: %s' % t.id)
    search.send_keys(yap.gui.Keys.ENTER)


def add_subtransaction_rows(t):
    memo = yap.gui.get_by_text('user-entered-text', t.id, count=1, partial=True)
    yap.gui.click(memo, 2)
    removes = yap.gui.get('ynab-grid-sub-remove', require=False, wait=1)
    while removes:
        yap.gui.click(removes)
        removes = yap.gui.get('ynab-grid-sub-remove', require=False, wait=.5)
    n = len(t.subtransactions)
    if n > 1:
        category_dropdown = yap.gui.get_by_placeholder('dropdown-text-field', 'category')
        category_dropdown.send_keys(' ')
        split = yap.gui.get('modal-account-categories-split-transaction')
        yap.gui.click(split)
        'yap.gui.clicking split means we already have two'
        for i in range(n - 2):
            yap.gui.click(yap.gui.get('ynab-grid-split-add-sub-transaction'))


def enter_transaction(t):
    locate_transaction(t)
    add_subtransaction_rows(t)
    account, date, payees, categories, memos = map(lambda p: yap.gui.get_by_placeholder('accounts-text-field', p),
                                                   ('account', 'date', 'payee', 'category', 'memo'))
    date.send_keys(t._date)
    outflows, inflows = map(lambda p: yap.gui.get_by_placeholder(
        'ember-text-field', p), ('outflow', 'inflow'))
    n = len(t.subtransactions)
    if n == 1:
        enter_item(t, payees, categories, memos, outflows)
        ' TODO: do not approve, only save '
        ' Maybe it is only approving things that are already approved? '
        approve = yap.gui.get_by_text('button-primary', ['Approve', 'Save'])
        if approve.text == 'Approve':
            yap.utils.log('Warning, approving...')
        yap.gui.click(approve)
    else:
        memos[0].send_keys(', '.join(s.memo for s in t.subtransactions))
        for i, s in enumerate(t.subtransactions):
            '+1 because index 0 is for overall purchase'
            enter_item(s, payees[i + 1], categories[i + 1], memos[i + 1], outflows[i + 1])
        outflows[-1].send_keys(yap.gui.Keys.ENTER)


def enter_all_transactions(transactions):
    for t in transactions:
        if len(t.subtransactions) > 3:
            yap.utils.log(
                'Skipping puchase with items for speed reasons during alpha test. Feel free to remove this check.')
            ' theta(len(items)^2) time, very tolerable at any reasonable n, but for testing, this is helpful'
            continue
        try:
            enter_transaction(t)
        except BaseException:
            ' Likely because there were multiple search results '
            yap.utils.log('Error on transaction', t)
            yap.utils.log(traceback.format_exc())
            search = yap.gui.get('transaction-search-input')
            search.clear()
    if yap.settings.close_browser_on_finish:
        yap.gui.driver().quit()
