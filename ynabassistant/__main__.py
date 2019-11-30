import ynabassistant as ya
import ynab_api


def main():
    ya.Assistant.download_all_ynab()
    #ya.test.restore_test_data.main()

if __name__ == '__main__':
    main()
