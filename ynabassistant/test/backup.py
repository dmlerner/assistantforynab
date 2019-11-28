import ynabassistant as ya


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


def download_and_compare(annotated):
    ya.utils.log_info('download_and_compare')
    ya.Assistant.download_ynab(transactions=True)
    downloaded = ya.assistant.utils.get_transactions(ya.settings.account_name)
    ya.utils.log_info('downloaded', *downloaded)
    diffs = ya.backup.utils.diff_transactions(downloaded, annotated)
    ya.utils.debug_assert(all(not x for x in diffs))
    for ts in annotated, downloaded:
        ts.sort(key=lambda t: t.date)
    diffs = ya.backup.utils.diff_transactions(downloaded, annotated)
    ya.utils.log_debug(*diffs)
    ya.utils.debug_assert(all(not x for x in diffs))


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
