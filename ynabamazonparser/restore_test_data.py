import ynabamazonparser as yap
import random
import time

yap.ynab.gui_client.load_gui()


def rename_and_close():
    yap.utils.log_debug('rename_and_close')
    try:
        edit_account = yap.gui.get_by_text('user-entered-text', yap.settings.account_name)
        yap.utils.log_debug(edit_account)
        yap.gui.right_click(edit_account)
        yap.gui.send_keys(str(random.random()))
        yap.gui.get('button-red').click()
        yap.gui.get_by_text('button-primary', 'Transfer Funds').click()
        yap.gui.get_by_text('button-primary', 'Finish Closing Account').click()
    except BaseException:
        yap.utils.log_exception()
        yap.utils.log_debug('probably already deleted')


def add_new_account():
    yap.utils.log_debug('add_new_account')
    time.sleep(1)
    add_account = yap.gui.get('nav-add-account')
    add_account.click()
    unlinked = yap.gui.get_by_text('select-linked-unlinked-box-title', 'UNLINKED')
    unlinked.click()
    yap.gui.send_keys('credit')
    yap.gui.send_keys(yap.gui.Keys.TAB)
    yap.gui.send_keys(yap.settings.account_name)
    yap.gui.send_keys(yap.gui.Keys.TAB)
    yap.gui.send_keys('0')
    yap.gui.send_keys(yap.gui.Keys.TAB)
    yap.gui.send_keys(yap.gui.Keys.ENTER)
    time.sleep(2)
    yap.gui.get_by_text('pull-right', 'Done').click()


def load_test_data():
    yap.utils.log_debug('load_test_data')
    '''
    account_id: str
    date: str
    amount: int
    payee_id: Optional[str] = None
    payee_name: Optional[str] = None
    category_id: Optional[str] = None
    memo: Optional[str] = None
    cleared: Optional[str] = None
    approved: Optional[bool] = None
    flag_color: Optional[str] = None
    import_id: Optional[str] = None
    '''
    ts = [t for t in yap.ynab.api_client.get_all_transactions().values() if t.account_name == 'Test Data']
    n = 30
    ts = ts[:n]
    yap.gui.get_by_text('user-entered-text', yap.settings.account_name).click()
    url = yap.gui.driver().current_url
    account_id = url[url.rindex('/') + 1:]
    for t in ts:
        t.account_id = account_id
    yap.ynab.api_client.create(ts)
    yap.utils.quit(True)


def prepare_test_account():
    yap.utils.log_debug('prepare_test_account')
    rename_and_close()
    add_new_account()
    load_test_data()


prepare_test_account()
