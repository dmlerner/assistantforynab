import ynabassistant as ya
import ynab_api


def main():
    #ya.backup.restore_account_transactions()
    #return ya.backup.load_before(ynab_api.TransactionDetail)
    ya.test.amazon.main()


if __name__ == '__main__':
    td = main()
