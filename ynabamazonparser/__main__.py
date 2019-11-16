from ynabamazonparser import assistant


def main():
    a = assistant.Assistant()
    a.load_amazon_data()
    a.load_ynab_data()
    a.update_amazon_transactions()
    a.update_ynab()


if __name__ == '__main__':
    main()
