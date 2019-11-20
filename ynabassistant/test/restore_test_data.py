import ynabassistant as ya
import random
import time



def rename_and_close():
    ya.utils.log_debug('rename_and_close')
    try:
        edit_account = ya.utils.gui.get_by_text('user-entered-text', ya.settings.account_name)
        ya.utils.log_debug(edit_account)
        ya.utils.gui.right_click(edit_account)
        ya.utils.gui.send_keys(str(random.random()))
        ya.utils.gui.get('button-red').click()
        ya.utils.gui.get_by_text('button-primary', 'Transfer Funds', wait=4).click()
        ya.utils.gui.get_by_text('button-primary', 'Finish Closing Account', wait=4).click()
    except BaseException:
        ya.utils.log_exception_debug()
        ya.utils.log_debug('probably already deleted or no transactions in account to transfer')


def add_new_account():
    ya.utils.log_debug('add_new_account')
    time.sleep(1)
    add_account = ya.utils.gui.get('nav-add-account')
    add_account.click()
    unlinked = ya.utils.gui.get_by_text('select-linked-unlinked-box-title', 'UNLINKED')
    unlinked.click()
    ya.utils.gui.send_keys('credit')
    ya.utils.gui.send_keys(ya.utils.gui.Keys.TAB)
    ya.utils.gui.send_keys(ya.settings.account_name)
    ya.utils.gui.send_keys(ya.utils.gui.Keys.TAB)
    ya.utils.gui.send_keys('0')
    ya.utils.gui.send_keys(ya.utils.gui.Keys.TAB)
    ya.utils.gui.send_keys(ya.utils.gui.Keys.ENTER)
    time.sleep(2)
    ya.utils.gui.get_by_text('pull-right', 'Done').click()


def load_test_data():
    ya.utils.log_debug('load_test_data')
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
    ts = [t for t in ya.ynab.api_client.get_all_transactions().values() if t.account_name == 'Test Data']
    n = 30
    ts = ts[:n]
    ya.utils.gui.get_by_text('user-entered-text', ya.settings.account_name).click()
    url = ya.utils.gui.driver().current_url
    account_id = url[url.rindex('/') + 1:]
    for t in ts:
        t.account_id = account_id
    ya.ynab.api_client.create(ts)
    ya.utils.quit(True)


def prepare_test_account():
    ya.utils.log_debug('prepare_test_account')
    try:
        rename_and_close()
        add_new_account()
        load_test_data()
    except BaseException:
        ya.utils.log_exception()
        ya.utils.quit(True)

if __name__ == '__main__':
    ya.ynab.gui_client.load_gui()
    prepare_test_account()
