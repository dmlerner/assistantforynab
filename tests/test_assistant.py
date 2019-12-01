import ynabassistant as ya


def main():
    ya.Assistant.download_all_ynab()
    ya.Assistant.load_amazon_data()
    ya.Assistant.update_amazon_transactions()
    ya.Assistant.update_ynab()


if __name__ == '__main__':
    main()
