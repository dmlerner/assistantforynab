import ynabassistant as ya

'''
Restore state for start of tests:
    Test data has unlabeled/unsplit
    Annotated has labeled/split
    Chase Amazon is empty
    No other accounts
'''


def delete_extra_accounts():
    whitelist = list(map(ya.Assistant.accounts.by_name, ('Test Data', 'Annotated')))
    to_delete = filter(lambda a: a not in whitelist, ya.Assistant.accounts)
    ya.ynab.queue_delete_accounts(to_delete)
    return whitelist


def main():
    ya.Assistant.download_ynab(accounts=True, transactions=True)
    test_data, annotated = delete_extra_accounts()
    ya.ynab.do()
    ya.Assistant.download_ynab(accounts=True)
    ya.ynab.queue_clone_account(test_data, ya.settings.account_name)
    ya.ynab.do()


if __name__ == '__main__':
    main()
