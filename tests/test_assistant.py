#import ynabassistant as ya
from ynabassistant.assistant.assistant import Assistant
import tests


def test():
    #tests.setup_data.main()
    Assistant.download_all_ynab()
    Assistant.load_amazon_data()
    Assistant.update_amazon_transactions()
    Assistant.update_ynab()


if __name__ == '__main__':
    test()
