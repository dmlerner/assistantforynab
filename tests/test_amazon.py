import assistantforynab
import tests


def test():
    a = assistantforynab.Assistant
    a.load_amazon_data()
    tests.setup_data.main()
    a.download_all_ynab()
    a.update_amazon_transactions()
    a.update_ynab()


if __name__ == '__main__':
    test()
