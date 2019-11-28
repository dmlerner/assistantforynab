import ynabassistant as ya


def load_gui():
    ya.utils.log_debug('load_gui')
    url = 'https://app.youneedabudget.com/%s/accounts' % ya.settings.budget_id
    d = ya.utils.gui.driver()
    d.get(url)
    if not ya.utils.gui.get('user-logged-in', require=False):
        selection = input('Must be logged in. Try again? [Y/n]')
        if selection.lower() != 'n':
            load_gui()


def enter_fields(fields, values):
    ya.utils.log_debug('enter_fields', fields, values)
    for i, (f, v) in enumerate(zip(fields, values)):
        f.clear()
        f.send_keys(str(v))
        f.send_keys(ya.utils.gui.Keys.TAB)


def get_category(st):
    ya.utils.log_debug('get_category', st)
    # TODO/BUG: "Return: Amazon" category is equivalent to "AnythingElse: Amazon"'
    # use cateogory group id?
    ya.ynab.utils.type_assert_st(st)
    category = st.__dict__.get('category_name')
    if not category or 'Split (Multiple' in category:
        assert ya.settings.default_category
        ya.utils.log_debug('invalid category %s, using default %s' % (str(category), ya.settings.default_category))
        '''
        ynab would fail to download with ynab_api_client if `st` is a split transaction
        even though you can hit save in the ui
        hence using a default
        '''
        return ya.settings.default_category
    return category


def get_payee(st):
    ya.utils.log_debug('get_payee', st)
    ya.ynab.utils.type_assert_st(st)
    return st.__dict__.get('payee_name')


def enter(st, payee_element, category_element, memo_element, outflow_element, inflow_element):
    ya.utils.log_debug('enter', st)
    ya.ynab.utils.type_assert_st(st)
    category = get_category(st)
    payee = get_payee(st)
    amount = ya.ynab.utils.amount(st)
    outflow = 0 if amount > 0 else abs(amount)
    inflow = 0 if amount < 0 else abs(amount)
    enter_fields((payee_element, category_element, memo_element, outflow_element),
                 (payee, category, st.memo, outflow, inflow))


def locate_transaction(t):
    ya.utils.log_debug('locate_transaction', t)
    search = ya.utils.gui.get('transaction-search-input')
    search.clear()
    search.send_keys('Account: %s, Memo: %s' % (t.account_name, t.id))
    search.send_keys(ya.utils.gui.Keys.ENTER)


def adjust_subtransaction_rows(t):
    ya.utils.log_debug('add_subtransactions_rows', len(t.subtransactions))
    # Remove existing subtransactions
    memo = ya.utils.gui.get_by_text('user-entered-text', t.id, count=1, partial=True)
    ya.utils.gui.click(memo, 2)
    removes = ya.utils.gui.get('ynab-grid-sub-remove', require=False, wait=1)
    while removes:
        ya.utils.gui.click(removes)
        removes = ya.utils.gui.get('ynab-grid-sub-remove', require=False, wait=.5)

    # Add rows for the new ones
    n = len(t.subtransactions)
    if n == 0:
        return
    ya.utils.gui.get_by_placeholder('accounts-text-field', 'category').clear()  # needed?
    category_dropdown = ya.utils.gui.get_by_placeholder('dropdown-text-field', 'category')
    category_dropdown.send_keys(' ')
    split = ya.utils.gui.get('modal-account-categories-split-transaction')
    ya.utils.gui.click(split)
    for i in range(n - 2):
        # gui.clicking split means we already have two
        ya.utils.gui.click(ya.utils.gui.get('ynab-grid-split-add-sub-transaction'))
    if n == 1:
        # which is weird but in principle OK
        ya.utils.gui.click(ya.utils.gui.get('ynab-grid-sub-remove'))
    assert len(ya.utils.gui.get('ynab-grid-sub-remove')) == n


def enter_transaction(t):
    ya.utils.log_debug('enter_transaction', t)
    accounts_sidebar = ya.utils.gui.get_by_text('user-entered-text', t.account_name)
    ya.utils.gui.click(accounts_sidebar)  # handles that it contains two elements
    locate_transaction(t)
    assert t.account_name not in ('Annotated', 'Test Data')  # don't overwrite test data
    adjust_subtransaction_rows(t)
    date, payees, categories, memos = map(lambda p: ya.utils.gui.get_by_placeholder('accounts-text-field', p),
                                          ('date', 'payee', 'category', 'memo'))
    date.send_keys(ya.ynab.utils.gui_format_date(t.date))
    outflows, inflows = map(lambda p: ya.utils.gui.get_by_placeholder(
        'ember-text-field', p), ('outflow', 'inflow'))
    if len(t.subtransactions) == 0:
        enter(t, payees, categories, memos, outflows, inflows)
        ' TODO: do not approve, only save? '
        ' Maybe it is only approving things that are already approved? '
        approve = ya.utils.gui.get_by_text('button-primary', ['Approve', 'Save'])
        ya.utils.log_debug('approve/save?', approve.text)
        ya.utils.gui.click(approve)
    else:
        for i, s in enumerate(t.subtransactions):
            enter(s, payees[i + 1], categories[i + 1], memos[i + 1], outflows[i + 1], inflows[i + 1])
        outflows[-1].send_keys(ya.utils.gui.Keys.ENTER)


def enter_all_transactions(transactions):
    ya.utils.log_debug('enter_all_transactions', len(transactions))
    for t in transactions:
        ya.utils.log_info(t)
        if len(t.subtransactions) > 3:
            ya.utils.log_info(
                '''Skipping puchase with %s items for speed reasons during alpha test.
                   Feel free to remove this check.''' % len(t.subtransactions)
            )
            continue
        try:
            enter_transaction(t)
        except BaseException:
            ' Likely because there were multiple search results '
            ya.utils.log_exception()
            ya.utils.log_error('Error on transaction', t)
            search = ya.utils.gui.get('transaction-search-input')
            search.clear()
    ya.utils.gui.quit()
