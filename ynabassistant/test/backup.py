import ynabassistant as ya
import time


def save_and_load_int():
    ya.utils.log_info('save_and_load_int')
    ya.backup.local.save(1)
    ya.backup.local.save(2)
    ya.utils.debug_assert(ya.backup.local.load(int) == [1, 2])


def save_and_load_anotated_transactions():
    ya.utils.log_info('save_and_load_annotated_transactions')
    annotated = ya.assistant.utils.get_transactions('Annotated')
    ya.utils.log_debug(*annotated)
    loaded = ya.backup.local.load_account_transactions('Annotated')
    ya.utils.debug_assert(annotated == loaded)
    ya.utils.debug_assert(str(annotated) == str(loaded))
    return annotated


def download_and_compare(annotated, wait=5, retries=2):
    ya.utils.log_info('download_and_compare', retries)
    ya.Assistant.download_ynab(transactions=True)
    downloaded = ya.assistant.utils.get_transactions(ya.settings.account_name)
    ya.utils.log_info('downloaded', *downloaded)
    for ts in annotated, downloaded:  # needed?
        ts.sort(key=lambda t: t.date)
    diffs = ya.backup.utils.diff_transactions(downloaded, annotated)
    diffs = [d for d in diffs if 'Starting Balance' not in str(d)]  # TODO
    ya.utils.log_debug(*diffs)
    if all(not x for x in diffs):
        return
    assert retries > 0
    ya.utils.log_info('failed, sleeping %s' % wait)
    time.sleep(wait)
    download_and_compare(annotated, wait, retries - 1)


def main():
    save_and_load_int()
    ya.ynab.gui_client.load_gui()
    ya.test.restore_test_data.rename_and_close()
    ya.test.restore_test_data.add_new_account()
    ya.utils.gui.quit()
    ya.Assistant.download_all_ynab()
    annotated = save_and_load_anotated_transactions()
    ya.backup.remote.copy_to_account(annotated, ya.settings.account_name)
    download_and_compare(annotated)
    ya.utils.log_info('PASS')


if __name__ == '__main__':
    main()
