import ynabassistant as ya
import copy


def save_and_load_int():
    ya.utils.log_info('save_and_load_int')
    ya.utils.backup.save(1)
    ya.utils.backup.save(2)
    assert ya.utils.backup.load(int) == [1, 2]


def save_and_load_anotated_transactions():
    ya.utils.log_info('save_and_load_annotated_transactions')
    annotated = [t for t in ya.assistant.Assistant.transactions.values() if t.account_name == 'Annotated']
    annotated.sort(key=lambda t: t.date)
    annotated = annotated[-30:]
    ya.utils.log_debug(*annotated)
    ya.utils.backup.save(annotated)
    loaded = ya.utils.backup.load(type(annotated[0]))
    assert annotated == loaded
    assert str(annotated) == str(loaded)
    return annotated


def upload_to_new_account(annotated):
    ya.utils.log_info('upload_to_new_account')
    to_upload = copy.deepcopy(annotated)
    account_ids = [id for (id, ac) in ya.assistant.Assistant.accounts.items() if ac.name == ya.settings.account_name]
    assert len(account_ids) == 1
    account_id = account_ids.pop()
    for t in to_upload:
        t.account_name = ya.settings.account_name  # matters to gui but not rest
        t.account_id = account_id
        t.import_id = None  # TODO maybe I need to poke the subtransactions like an amazon/amazon.annotate
    ya.utils.log_info('to_upload', *to_upload)
    ya.ynab.queue_create(to_upload)
    ya.ynab.do()


def download_and_compare(annotated):
    ya.utils.log_info('download_and_compare')
    downloaded = [t for t in ya.ynab.api_client.get_all_transactions() if t.account_name == ya.settings.account_name]
    downloaded.sort(key=lambda t: t.date)
    downloaded = downloaded[-30:]
    ya.utils.log_info('downloaded', *downloaded)
    def f(x): return set(y.__dict__['_' + x] for y in downloaded) - set(y.__dict__['_' + x] for y in annotated)
    def g(x): return set(y.__dict__['_' + x] for y in annotated) - set(y.__dict__['_' + x] for y in downloaded)
    def h(x): return (f(x), g(x))
    ya.utils.log_info(*h('amount'))
    ya.utils.log_info(*h('memo'))
    ya.utils.log_info(*h('date'))
    # ya.utils.debug()
    assert annotated == downloaded  # will fail because ids, TODO


def main():
    save_and_load_int()
    ya.ynab.gui_client.load_gui()
    ya.test.restore_test_data.rename_and_close()
    ya.test.restore_test_data.add_new_account()
    ya.utils.gui.quit()
    ya.assistant.Assistant.load_ynab_data()
    annotated = save_and_load_anotated_transactions()
    upload_to_new_account(annotated)
    download_and_compare(annotated)
    ya.utils.log_info('PASS')


if __name__ == '__main__':
    main()
