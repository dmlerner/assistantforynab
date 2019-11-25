import ynabassistant as ya


def save_and_load_int():
    ya.utils.log_info('save_and_load_int')
    ya.backup.local.save(1)
    ya.backup.local.save(2)
    assert ya.backup.local.load(int) == [1, 2]


def save_and_load_anotated_transactions():
    ya.utils.log_info('save_and_load_annotated_transactions')
    annotated = [t for t in ya.Assistant.transactions.values() if t.account_name == 'Annotated']
    annotated.sort(key=lambda t: t.date)
    ya.utils.log_debug(*annotated)
    ya.backup.local.save(annotated)
    loaded = ya.backup.local.load(type(annotated[0]))
    assert annotated == loaded
    assert str(annotated) == str(loaded)
    return annotated


def download_and_compare(annotated):
    ya.utils.log_info('download_and_compare')
    downloaded = [t for t in ya.ynab.api_client.get_all_transactions() if t.account_name == ya.settings.account_name]
    downloaded.sort(key=lambda t: t.date)
    ya.utils.log_info('downloaded', *downloaded)
    assert all(not x for x in ya.backup.utils.diff_transactions(downloaded, annotated))


def main():
    save_and_load_int()
    ya.ynab.gui_client.load_gui()
    ya.test.restore_test_data.rename_and_close()
    ya.test.restore_test_data.add_new_account()
    ya.utils.gui.quit()
    ya.Assistant.load_ynab_data()
    annotated = save_and_load_anotated_transactions()
    ya.backup.remote.copy_to_account(annotated, ya.settings.account_name)
    download_and_compare(annotated)
    ya.utils.log_info('PASS')


if __name__ == '__main__':
    main()
