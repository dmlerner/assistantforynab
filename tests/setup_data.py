from ynabassistant.ynab import ynab
from ynabassistant import settings
from ynabassistant.assistant import Assistant
import sys

'''
Restore state for start of tests:
    Test data has unlabeled/unsplit
    Annotated has labeled/split
    Chase Amazon is empty
    No other accounts
'''


def delete_extra_accounts():
    if settings.get('budget_id') == '7b027e9b-4ed8-495e-97bd-f0339357adf0':
        print('IDIOT YOU ALMOST DELETED THE REAL ACCOUNT\n' * 10)
        sys.exit()
    whitelist = list(map(Assistant.accounts.by_name, ('Test Data', 'Annotated')))
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
