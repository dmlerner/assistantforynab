import ynabassistant as ya
import time


def save_and_load_int():
    ya.utils.log_info('save_and_load_int')
    ya.backup.local.store(1)
    ya.backup.local.store(2)
    assert ya.backup.local.load(int) == [1, 2]


def save_and_load_anotated_transactions():
    ya.utils.log_info('save_and_load_annotated_transactions')
    ya.Assistant.download_all_ynab()
    annotated = ya.Assistant.transactions.by_name('Annotated')
    ya.utils.log_debug(annotated, len(annotated))
    loaded = ya.backup.local.load_account_transactions('Annotated', -1)
    ya.utils.log_debug(loaded, len(loaded))
    assert annotated == loaded
    return annotated


def download_and_compare(annotated, wait=5, retries=2):
    ya.utils.log_info('download_and_compare', retries)
    ya.Assistant.download_ynab(transactions=True)
    downloaded = ya.Assistant.transactions.by_name(ya.settings.account_name)
    downloaded = list(filter(lambda t: t.payee_name != 'Starting Balance', downloaded)
                      )  # TODO maybe this should be removed by clone
    ya.utils.log_info('downloaded', *downloaded)
    for ts in annotated, downloaded:  # needed?
        ts.sort(key=lambda t: t.date)
    diffs = ya.backup.utils.diff_transactions(downloaded, annotated)
    ya.utils.log_debug(*diffs)
    if all(not x for x in diffs):
        return
    assert retries > 0
    ya.utils.log_info('failed, sleeping %s' % wait)
    time.sleep(wait)
    download_and_compare(annotated, wait, retries - 1)


def test():
    save_and_load_int()
    ya.Assistant.download_all_ynab()  # TODO probably don't need all of that
    ya.test.test_data_setup.delete_extra_accounts()
    ya.ynab.do()
    # ya.utils.gui.quit()
    annotated = save_and_load_anotated_transactions()
    new_account = ya.ynab.add_unlinked_account(ya.settings.account_name)
    ya.ynab.queue_copy_to_account(annotated, new_account)
    ya.ynab.do()
    download_and_compare(annotated)


if __name__ == '__main__':
    test()
