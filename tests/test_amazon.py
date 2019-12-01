import ynabassistant 
import tests


def test():
    tests.test_data_setup.test()
    a = ynabassistant.Assistant
    a.download_all_ynab()
    a.load_amazon_data()
    a.update_amazon_transactions()
    a.update_ynab()


if __name__ == '__main__':
    test()
