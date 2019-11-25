import ynabamazonparser as ya


def main():
    ya.Assistant.load_ynab_data()
    ya.Assistant.load_amazon_data()
    ya.Assistant.update_amazon_transactions()
    ya.Assistant.update_ynab()


if __name__ == '__main__':
    main()
