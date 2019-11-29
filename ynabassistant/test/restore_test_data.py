import ynabassistant as ya

'''
Restore state for start of tests:
    Test data has unlabeled/unsplit
    Annotated has labeled/split
    Chase Amazon is empty
    No other accounts
'''

def delete_extra_accounts():
    account_names = set(ya.assistant.utils._accounts.keys())
    whitelist = {'Test Data', 'Annotated'}
    to_delete = list(filter(lambda n: n not in whitelist, account_names))
    # TODO: WTF is the differencein ya.ynab.do and ya.ynab.ynab.do? appears we have two copie sof things?
    ya.ynab.queue_delete_accounts(list(map(ya.assistant.utils.get_account, to_delete)))


def load_test_data():
    ya.utils.log_debug('load_test_data')
    ts = ya.assistant.utils.get_transactions('Test Data')
    n = 30
    ts = ts[:n]
    ya.utils.gui.get_by_text('user-entered-text', ya.settings.account_name).click()
    url = ya.utils.gui.driver().current_url
    account_id = url[url.rindex('/') + 1:]
    for t in ts:
        t.account_id = account_id  # notice that we don't overwrite account_name, and rest prefers ID, ignores name
    ya.ynab.api_client.create_transactions(ts)
    ya.utils.gui.quit()


def main():
    ya.Assistant.download_ynab(accounts=True, transactions=True)
    delete_extra_accounts()
    ya.ynab.do()
    ya.ynab.gui_client.add_unlinked_account(ya.settings.account_name)
    prepare_test_account()


if __name__ == '__main__':
    main()
