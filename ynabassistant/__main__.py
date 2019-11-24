import ynabassistant as ya
import ynab_api


def main():
    ya.utils.backup.restore_account_transactions()
    #return ya.utils.backup.load_before(ynab_api.TransactionDetail)


if __name__ == '__main__':
    td = main()
