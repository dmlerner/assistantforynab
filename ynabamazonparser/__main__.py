from ynabamazonparser import utils, amazon, match
from ynab import api_client, gui_client
from amazon import downloader
import pdb


def main():
    utils.log('Loading amazon data')
    amazon_data = downloader.load_all()
    utils.log('got data', [(k, len(amazon_data[k])) for k in amazon_data])
    utils.log('Downloading transactions from your ynab')
    transactions = api_client.get_transactions_to_update()
    utils.log('Matching amazon data to the transactions')
    utils.log('uhhh', [(k, len(amazon_data[k])) for k in amazon_data], len(amazon_data['orders']))
#    pdb.set_trace()
    orders_by_transaction_id = match.match_all(
        transactions, amazon_data['orders'])
    utils.log('Putting order ids as ynab memo to can find them in the gui')
    api_client.update_all(transactions, orders_by_transaction_id)
    utils.log('Entering all the information in the gui via Selenium/Chrome')
    gui_client.enter_all_transactions(
        transactions, orders_by_transaction_id)
    utils.quit()


if __name__ == '__main__':
    main()
