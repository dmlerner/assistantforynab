import time
import settings
import ynab
from ynabassistant.utils import utils


def load_gui():
    utils.log_debug('load_gui')
    url = 'https://app.youneedabudget.com/%s/accounts' % settings.budget_id
    d = utils.gui.driver()
    if url in d.current_url:
        return
    d.get(url)
    if not utils.gui.get('user-logged-in', require=False):
        selection = input('Must be logged in. Try again? [Y/n]')
        if selection.lower() != 'n':
            load_gui()


def enter_fields(fields, values):
    utils.log_debug('enter_fields', fields, values)
    for i, (f, v) in enumerate(zip(fields, values)):
        f.clear()
        f.send_keys(str(v))
        f.send_keys(utils.gui.Keys.TAB)


def get_category(st):
    utils.log_debug('get_category', st)
    # TODO/BUG: "Return: Amazon" category is equivalent to "AnythingElse: Amazon"'
    # use cateogory group id?
    ynab.utils.type_assert_st(st)
    category = st.__dict__.get('category_name')
    if not category or 'Split (Multiple' in category:
        assert settings.default_category
        utils.log_debug('invalid category %s, using default %s' % (str(category), settings.default_category))
        '''
        ynab would fail to download with ynab_api_client if `st` is a split transaction
        even though you can hit save in the ui
        hence using a default
        '''
        return settings.default_category
    return category


def get_payee(st):
    utils.log_debug('get_payee', st)
    ynab.utils.type_assert_st(st)
    return st.__dict__.get('payee_name')


def enter(st, payee_element, category_element, memo_element, outflow_element, inflow_element):
    utils.log_debug('enter', st)
    ynab.utils.type_assert_st(st)
    category = get_category(st)
    payee = get_payee(st)
    amount = ynab.utils.amount(st)
    outflow = 0 if amount > 0 else abs(amount)
    inflow = 0 if amount < 0 else abs(amount)
    enter_fields((payee_element, category_element, memo_element, outflow_element),
                 (payee, category, st.memo, outflow, inflow))


def locate_transaction(t):
    utils.log_debug('locate_transaction', t)
    search('Account: %s, Memo: %s' % (t.account_name, t.id))


def search(query):
    utils.log_debug('search', query)
    search = utils.gui.get('transaction-search-input')
    search.clear()
    search.send_keys(query)
    search.send_keys(utils.gui.Keys.ENTER)


def select_all():
    utils.gui.click(utils.gui.get('ynab-checkbox-button-square'))


def adjust_subtransaction_rows(t):
    utils.log_debug('add_subtransactions_rows', len(t.subtransactions))
    # Remove existing subtransactions
    memo = utils.gui.get_by_text('user-entered-text', t.id, count=1)  # TODO: why was this partial?
    utils.gui.click(memo, 2)
    removes = utils.gui.get('ynab-grid-sub-remove', require=False, wait=1)
    while removes:
        utils.gui.click(removes)
        removes = utils.gui.get('ynab-grid-sub-remove', require=False, wait=.5)

    # Add rows for the new ones
    n = len(t.subtransactions)
    if n == 0:
        return
    utils.gui.get_by_placeholder('accounts-text-field', 'category').clear()  # needed?
    category_dropdown = utils.gui.get_by_placeholder('dropdown-text-field', 'category')
    category_dropdown.send_keys(' ')
    split = utils.gui.get('modal-account-categories-split-transaction')
    utils.gui.click(split)
    for i in range(n - 2):
        # gui.clicking split means we already have two
        utils.gui.click(utils.gui.get('ynab-grid-split-add-sub-transaction'))
    if n == 1:
        # which is weird but in principle OK
        utils.gui.click(utils.gui.get('ynab-grid-sub-remove'))
    assert len(utils.gui.get('ynab-grid-sub-remove')) == n


def enter_transaction(t):
    utils.log_debug('enter_transaction', t)
    accounts_sidebar = utils.gui.get_by_text('user-entered-text', t.account_name)
    utils.gui.click(accounts_sidebar)  # handles that it contains two elements
    locate_transaction(t)
    assert t.account_name not in ('Annotated', 'Test Data')  # don't overwrite test data
    adjust_subtransaction_rows(t)
    date, payees, categories, memos = map(lambda p: utils.gui.get_by_placeholder('accounts-text-field', p),
                                          ('date', 'payee', 'category', 'memo'))
    date.send_keys(ynab.utils.gui_format_date(t.date))
    outflows, inflows = map(lambda p: utils.gui.get_by_placeholder(
        'ember-text-field', p), ('outflow', 'inflow'))
    if len(t.subtransactions) == 0:
        enter(t, payees, categories, memos, outflows, inflows)
        ' TODO: do not approve, only save? '
        ' Maybe it is only approving things that are already approved? '
        approve = utils.gui.get_by_text('button-primary', ['Approve', 'Save'])
        utils.log_debug('approve/save?', approve.text)
        utils.gui.click(approve)
    else:
        for i, s in enumerate(t.subtransactions):
            enter(s, payees[i + 1], categories[i + 1], memos[i + 1], outflows[i + 1], inflows[i + 1])
        outflows[-1].send_keys(utils.gui.Keys.ENTER)


@utils.listy
def enter_all_transactions(transactions):
    utils.log_debug('enter_all_transactions', len(transactions))
    load_gui()
    for t in transactions:
        utils.log_info(t)
        if len(t.subtransactions) > 300:
            utils.log_info(
                '''Skipping puchase with %s items for speed reasons during alpha test.
                   Feel free to remove this check.''' % len(t.subtransactions)
            )
            continue
        try:
            enter_transaction(t)
        except BaseException:
            ' Likely because there were multiple search results '
            utils.log_exception()
            utils.log_error('Error on transaction', t)
            search = utils.gui.get('transaction-search-input')
            search.clear()
    utils.gui.quit()


def add_unlinked_account(account_name, balance=0, account_type='credit'):
    utils.log_debug('add_unlinked_account')
    assert account_type in {'credit'}
    load_gui()
    # TODO: other account types? linked?
    time.sleep(1)
    add_account = utils.gui.get('nav-add-account')
    add_account.click()
    unlinked = utils.gui.get_by_text('select-linked-unlinked-box-title', 'UNLINKED')
    unlinked.click()
    utils.gui.send_keys(account_type)
    utils.gui.send_keys(utils.gui.Keys.TAB)
    utils.gui.send_keys(account_name)
    utils.gui.send_keys(utils.gui.Keys.TAB)
    utils.gui.send_keys(str(balance))
    utils.gui.send_keys(utils.gui.Keys.TAB)
    utils.gui.send_keys(utils.gui.Keys.ENTER)
    time.sleep(2)
    utils.gui.get_by_text('pull-right', 'Done').click()


def delete_transactions():
    load_gui()
    search('Memo: ' + ynab.ynab.delete_key)
    if not isinstance(utils.gui.get('ynab-checkbox-button-square'), list):
        return  # Means no transactions in results to delete, because only one element
    select_all()
    utils.gui.send_keys(utils.gui.Keys.TAB)
    utils.gui.send_keys(utils.gui.Keys.TAB)
    utils.gui.send_keys(utils.gui.Keys.DELETE)
    # Only gives confirm modal over some number of transactions. TODO: cut down this wait.
    confirm_delete = utils.gui.get_by_text('button-primary', 'Delete', require=False, wait=7)
    if confirm_delete:
        utils.gui.click(confirm_delete)


@utils.listy
def delete_accounts(accounts):
    utils.log_info('Deleting %s accounts via Web App' % len(accounts))
    load_gui()
    navlink_accounts = utils.gui.get('navlink-accounts')
    utils.gui.scroll_to(navlink_accounts)
    utils.gui.click(navlink_accounts)
    for a in accounts:
        edit_account = utils.gui.get_by_text('nav-account-name', a.name)
        utils.log_debug(edit_account)
        utils.gui.scroll_to(edit_account)
        utils.gui.right_click(edit_account)
        utils.gui.get_by_text('button-red', ['Close Account', 'Delete', 'Delete Account'], partial=True).click()
