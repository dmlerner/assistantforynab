from assistantforynab.ynab import ynab
from assistantforynab import settings, utils
from assistantforynab.assistant import Assistant

'''
Restore state for start of tests:
    Test data has unlabeled/unsplit
    Annotated has labeled/split
    Chase Amazon is empty
    No other accounts
'''


def delete_extra_accounts():
    whitelist = list(map(Assistant.accounts.by_name, ('Test Data', 'Annotated')))
    utils.log_info('WARNING: THIS WILL DELETE ALL ACCOUNTS EXCEPT %s!!!' % whitelist)
    confirm = input('Type "confirm" to confirm') == 'confirm'
    if not confirm:
        return
    to_delete = filter(lambda a: a not in whitelist, Assistant.accounts)
    ynab.queue_delete_accounts(to_delete)
    return whitelist


def main():
    ynab.api_client.init()
    Assistant.download_ynab(accounts=True, transactions=True)
    test_data, annotated = delete_extra_accounts()
    ynab.do()
    Assistant.download_ynab(accounts=True)
    ynab.queue_clone_account(test_data, settings.account_name)
    ynab.do()


if __name__ == '__main__':
    main()
