import ynabamazonparser as yap


def main():
    '''
    a = yap.assistant.Assistant()
    a.load_amazon_data()
    a.load_ynab_data()
    a.update_amazon_transactions()
    a.update_ynab()
    yap.utils.log_info('Success')
    '''
    categories = yap.ynab.api_client.get_categories()
    return categories


if __name__ == '__main__':
    cat=main()
