import traceback

from ynabamazonparser import utils, amazon, match, ynab, gui
from ynabamazonparser.config import settings


def load_gui():
    url = 'https://app.youneedabudget.com/%s/accounts' % settings.budget_id
    d = gui.driver()
    d.get(url)
    if not gui.get('user-logged-in'):
        selection = input(
            'please log in then press any key to continue, or q to quit').lower()
        if selection == 'q':
            utils.quit()
        load_gui()


def enter_fields(fields, values):
    ' TODO: could this be simpler? is that last tab actually a problem? '
    for i, (f, v) in enumerate(zip(fields, values)):
        f.clear()
        f.send_keys(str(v))
        if i != len(fields) - 1:
            f.send_keys(gui.Keys.TAB)


def get_category(transaction, item):
    if not transaction.category_name or 'Split (Multiple' in transaction.category_name:
        utils.log('Warning: invalid category %s' % transaction.category_name)
        ' ynab will fail to download with ynab_api_client if `transaction` is a split transaction '
        ' even though you can hit save in the ui '
        assert settings.default_category
        return settings.default_category
    return transaction.category_name


def enter_item(transaction, item, payee_element, category_element, memo_element, outflow_element):
    'TODO: payee based on item'
    'TODO: category based on item'
    'TODO/BUG: "Return: Amazon" category is equivalent to "AnythingElse: Amazon"'
    'TODO: proportional split of shipping, discounts or similar'
    category = get_category(transaction, item)
    enter_fields((payee_element, category_element, memo_element, outflow_element),
                 (transaction.payee_name, category, item.title, item.item_total))


def enter_transaction(transaction, items):
    assert transaction and items
    item_total = sum(i.item_total for i in items)
    assert utils.equalish(transaction.amount, item_total)

    search = gui.get('transaction-search-input')
    search.clear()
    search.send_keys('Memo: %s, Account: %s' %
                     (transaction.memo, settings.account_name))
    search.send_keys(gui.Keys.ENTER)
    memo = gui.get_by_text('user-entered-text', transaction.memo, count=1)
    gui.click(memo, 2)
    removes = gui.get('ynab-grid-sub-remove', require=False, wait=1)
    while removes:
        gui.click(removes)
        removes = gui.get('ynab-grid-sub-remove', require=False, wait=.5)
    if len(items) > 1:
        category_dropdown = gui.get_by_placeholder(
            'dropdown-text-field', 'category')
        category_dropdown.send_keys(' ')
        split = gui.get('modal-account-categories-split-transaction')
        gui.click(split)
        'gui.clicking split means we already have two'
        for i in range(len(items) - 2):
            gui.click(gui.get('ynab-grid-split-add-sub-transaction'))
    account, date, payees, categories, memos = map(lambda p: gui.get_by_placeholder('accounts-text-field', p),
                                                   ('account', 'date', 'payee', 'category', 'memo'))
    outflows, inflows = map(lambda p: gui.get_by_placeholder(
        'ember-text-field', p), ('outflow', 'inflow'))
    if len(items) == 1:
        enter_item(transaction, items[0], payees, categories, memos, outflows)
        ' TODO: do not approve, only save '
        ' Maybe it is only approving things that are already approved? '
        approve = gui.get_by_text('button-primary', ['Approve', 'Save'])
        if approve.text == 'Approve':
            utils.log('Warning, approving...')
        gui.click(approve)
    else:
        memos[0].send_keys(', '.join(i.title for i in items))
        for i, item in enumerate(items):
            '+1 because index 0 is for overall purchase'
            enter_item(transaction, item,
                       payees[i+1], categories[i+1], memos[i+1], outflows[i+1])
        outflows[-1].send_keys(gui.Keys.ENTER)


def enter_all_transactions(transactions, orders_by_transaction_id):
    load_gui()
    items_by_order_id = amazon.downloader.get_items_by_order_id()
    for t in transactions:
        if t.id not in orders_by_transaction_id:
            continue
        utils.log('Entering items for transaction',
                  orders_by_transaction_id[t.id])
        order = orders_by_transaction_id[t.id]
        utils.log('order', order)
        items = items_by_order_id[order.order_id]
        utils.log('items', items)
        if len(items) > 300:
            utils.log(
                'Skipping puchase with items for speed reasons during alpha test. Feel free to remove this check.')
            ' theta(len(items)^2) time, very tolerable at any reasonable n, but for testing, this is helpful'
            continue
        try:
            enter_transaction(t, items)
        except:
            ' Likely because there were multiple search results '
            utils.log('Error on transaction', t, items)
            utils.log(traceback.format_exc())
            search = gui.get('transaction-search-input')
            search.clear()
    if settings.close_browser_on_finish:
        gui.driver().quit()
