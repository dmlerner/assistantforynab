from ynabamazonparser import utils, match
from ynab import api_client, gui_client
from amazon import downloader


def main():
    separator = '\n' + '.' * 100 + '\n'

    utils.log('Loading Amazon')
    orders = downloader.load('orders')
    items = downloader.load('items')
    utils.log(separator)

    utils.log('Downloading YNAB')
    transactions = api_client.get_transactions_to_update()
    utils.log(separator)

    utils.log('Matching')
    orders_by_transaction_id, items_by_order_id = match.match_all(transactions, orders, items)
    if not orders_by_transaction_id:
        utils.log('No matching orders')
        utils.quit()
    utils.log(separator)

    utils.log('Putting order ids as ynab memo to can find them in the gui')
    api_client.update_all(transactions)
    utils.log(separator)

    utils.log('Entering all the information in the gui via Selenium/Chrome')
    gui_client.enter_all_transactions(
        transactions, orders_by_transaction_id, items_by_order_id)
    utils.log(separator)

    utils.quit()


if __name__ == '__main__':
    main()
