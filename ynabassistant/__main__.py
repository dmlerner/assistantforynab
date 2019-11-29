import ynabassistant as ya
import ynab_api


def main():
    ya.Assistant.download_ynab(transactions=True, accounts=True)
    account_names = set(ya.assistant.utils._accounts.keys())
    chase = list(filter(lambda n: 'Chase Amazon' in n, account_names))
    ya.utils.log_info('len chase', len(chase))
    for i, name in enumerate(chase):
        ts = ya.assistant.utils.get_transactions(name)
        ya.utils.log_info('len(ts)', ts and len(ts), name)
        ya.utils.log_debug('ts', ts)
        if ts:
            ya.ynab.ynab.queue_delete(ts)
        if i == len(chase) - 1:
            ya.ynab.ynab.do()
        if i == 0:
            continue
        if i % 10 == 0:
            ya.ynab.ynab.do()


if __name__ == '__main__':
    main()
