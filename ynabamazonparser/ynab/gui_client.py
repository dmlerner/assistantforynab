import datetime
import traceback
import os
import sys
import pdb
import time

import settings
import utils
import amazon_downloader
import match
import ynab_api_client


def load_gui():
    url = 'https://app.youneedabudget.com/%s/accounts' % settings.budget_id
    d = utils.driver()
    d.get(url)  
    if not get('user-logged-in'):
        selection = input('please log in then press any key to continue, or q to quit').lower()
        if selection == 'q':
            utils.quit()
        load_gui()

def enter_fields(fields, values):
    ' TODO: could this be simpler? is that last tab actually a problem? '
    for i, (f, v) in enumerate(zip(fields, values)):
        f.clear()
        f.send_keys(str(v))
        if i != len(fields) - 1:
            f.send_keys(Keys.TAB)

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
            (transaction.payee_name, category, item['Title'], item['Item Total']))


def enter_transaction(transaction, items):
    assert transaction and items
    transaction_total = utils.float_from_ynab_price(transaction.amount)
    item_total = sum(utils.float_from_amazon_price(i['Item Total']) for i in items)
    assert utils.equalish(transaction_total, item_total)

    search = get('transaction-search-input')
    search.clear()
    search.send_keys('Memo: %s, Account: %s' % (transaction.memo, settings.account_name))
    search.send_keys(Keys.ENTER)
    memo = get_by_text('user-entered-text', transaction.memo, count=1)
    click(memo, 2)
    removes = get('ynab-grid-sub-remove', require=False, wait=1)
    while removes:
        click(removes)
        removes = get('ynab-grid-sub-remove', require=False, wait=.5)
    if len(items) > 1:
        category_dropdown = get_by_placeholder('dropdown-text-field', 'category')
        category_dropdown.send_keys(' ')
        split = get('modal-account-categories-split-transaction')
        click(split)
        'clicking split means we already have two'
        for i in range(len(items) - 2):
            click(get('ynab-grid-split-add-sub-transaction'))
    account, date, payees, categories, memos =  map(lambda p: get_by_placeholder('accounts-text-field', p),
        ('account', 'date', 'payee', 'category', 'memo'))
    outflows, inflows = map(lambda p: get_by_placeholder('ember-text-field', p), ('outflow', 'inflow'))
    if len(items) == 1:
        enter_item(transaction, items[0], payees, categories, memos, outflows)
        ' TODO: do not approve, only save '
        ' Maybe it is only approving things that are already approved? '
        approve = get_by_text('button-primary', ['Approve', 'Save'])
        if approve.text == 'Approve':
            utils.log('Warning, approving...')
        click(approve)
    else:
        memos[0].send_keys(', '.join(i['Title'] for i in items))
        for i, item in enumerate(items):
            '+1 because index 0 is for overall purchase'
            enter_item(transaction, item, payees[i+1], categories[i+1], memos[i+1], outflows[i+1])
        outflows[-1].send_keys(Keys.ENTER)

def enter_all_transactions(transactions, orders_by_transaction_id):
    load_gui()
    items_by_order_id = amazon_downloader.get_items_by_order_id()
    for t in transactions:
        if t.id not in orders_by_transaction_id:
            continue
        utils.log('Entering items for transaction', orders_by_transaction_id[t.id])
        order = orders_by_transaction_id[t.id]
        utils.log('order', order)
        items = items_by_order_id[order['Order ID']]
        utils.log('items', items)
        if len(items) > 300:
            utils.log('Skipping puchase with items for speed reasons during alpha test. Feel free to remove this check.')
            ' theta(len(items)^2) time, very tolerable at any reasonable n, but for testing, this is helpful'
            continue
        try:
            enter_transaction(t, items)
        except:
            ' Likely because there were multiple search results '
            utils.log('Error on transaction', t, items)
            utils.log(traceback.format_exc())
            search = get('transaction-search-input')
            search.clear()
    if settings.close_browser_on_finish:
        utils.driver().quit()

