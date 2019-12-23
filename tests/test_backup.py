import assistantforynab as afy
from tests import setup_data
import time


def save_and_load_int():
    afy.utils.log_info('save_and_load_int')
    afy.backup.local.store(1)
    afy.backup.local.store(2)
    assert afy.backup.local.load(int) == [1, 2]


def save_and_load_anotated_transactions():
    afy.utils.log_info('save_and_load_annotated_transactions')
    afy.Assistant.download_all_ynab()
    annotated = afy.Assistant.transactions.by_name('Annotated')
    afy.utils.log_debug(annotated, len(annotated))
    loaded = afy.backup.local.load_account_transactions('Annotated', -1)
    afy.utils.log_debug(loaded, len(loaded))
    assert annotated == loaded
    return annotated


def download_and_compare(annotated, wait=5, retries=2):
    afy.utils.log_info('download_and_compare', retries)
    afy.Assistant.download_ynab(transactions=True)
    downloaded = afy.Assistant.transactions.by_name(afy.settings.account_name)
    downloaded = list(filter(lambda t: t.payee_name != 'Starting Balance', downloaded)
                      )  # TODO maybe this should be removed by clone
    afy.utils.log_info('downloaded', *downloaded)
    for ts in annotated, downloaded:  # needed?
        ts.sort(key=lambda t: t.date)
    diffs = afy.backup.diff_transactions(downloaded, annotated)
    afy.utils.log_debug(*diffs)
    if all(not x for x in diffs):
        return
    assert retries > 0
    afy.utils.log_info('failed, sleeping %s' % wait)
    time.sleep(wait)
    download_and_compare(annotated, wait, retries - 1)


def test():
    save_and_load_int()
    afy.Assistant.download_all_ynab()  # TODO probably don't need all of that
    setup_data.delete_extra_accounts()
    afy.ynab.ynab.do()
    # afy.utils.gui.quit()
    annotated = save_and_load_anotated_transactions()
    new_account = afy.ynab.ynab.add_unlinked_account(afy.settings.account_name)
    afy.ynab.ynab.queue_copy_to_account(annotated, new_account)
    afy.ynab.ynab.do()
    download_and_compare(annotated)


if __name__ == '__main__':
    test()
