import ynabassistant as ya


def main():
    ya.test.restore_test_data.main()
    a = ya.assistant.Assistant()
    a.load_amazon_data()
    a.load_ynab_data()
    a.update_amazon_transactions()
    a.update_ynab()


if __name__ == '__main__':
    main()
