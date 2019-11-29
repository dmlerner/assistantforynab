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


def main():
    ya.Assistant.download_ynab(accounts=True, transactions=True)
    delete_extra_accounts()
    ya.ynab.do()
    ya.Assistant.download_ynab(accounts=True)
    ya.ynab.queue_clone_account(ya.assistant.utils.get_account('Test Data'), ya.settings.account_name)
    ya.ynab.do()


if __name__ == '__main__':
    main()
