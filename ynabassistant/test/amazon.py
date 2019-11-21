import ynabassistant as ya


def main():
    a = ya.assistant.Assistant()
    a.load_amazon_data()
    a.load_ynab_data()
    a.update_amazon_transactions()
    a.update_ynab()
    ya.utils.log_info('Success')


if __name__ == '__main__':
    main()
