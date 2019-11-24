import ynabassistant as ya
import copy
import time


def save_and_load_int():
    ya.utils.log_info('save_and_load_int')
    ya.utils.backup.save(1)
    ya.utils.backup.save(2)
    assert ya.utils.backup.load(int) == [1, 2]


def save_and_load_anotated_transactions():
    ya.utils.log_info('save_and_load_annotated_transactions')
    annotated = [t for t in ya.assistant.Assistant.transactions.values() if t.account_name == 'Annotated']
    annotated.sort(key=lambda t: t.date)
    #annotated = annotated[-30:]
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
        for s in t.subtransactions:
            if s.payee_id:
                assert s.payee_id in ya.assistant.Assistant.payees
                s.payee_name = ya.assistant.Assistant.payees[s.payee_id].name
    ya.utils.log_info('to_upload', *to_upload)
    ya.ynab.queue_create(to_upload)
    ya.ynab.do()


def to_tuple(t):
    return t.amount, t.approved, t.category_id, t.category_name, t.cleared, t.date, \
        t.deleted, t.flag_color, t.memo, t.payee_id, t.payee_name, t.transfer_account_id


def sub_to_tuple(s):
    return s.amount, s.category_id, s.deleted, s.memo, s.payee_id, s.transfer_account_id


# def diff_tuples(t1, t2):
    # return ((i, j) for (i, j) in zip(t1, t2) if i != j)


def diff(ts1, ts2, tupler):
    tuple_ts1 = set(map(tupler, ts1))
    tuple_ts2 = set(map(tupler, ts2))
    return tuple_ts1 - tuple_ts2, tuple_ts2 - tuple_ts1


def download_and_compare(annotated):
    ya.utils.log_info('download_and_compare')
    downloaded = [t for t in ya.ynab.api_client.get_all_transactions() if t.account_name == ya.settings.account_name]
    downloaded.sort(key=lambda t: t.date)
    ya.utils.log_info('downloaded', *downloaded)
    dad, dda = diff(annotated, downloaded, to_tuple)
    ya.utils.log_debug(*dad)  # currently failing only on category_name/id
    ya.utils.log_debug(*dda)
    sdad, sdda = diff([s for t in annotated for s in t.subtransactions],
                      [s for t in downloaded for s in t.subtransactions], sub_to_tuple)
    ya.utils.log_debug(*sdad)
    ya.utils.log_debug(*sdda)
    assert not dad  # diff annotated downloaded
    assert not dda
    assert not sdad
    assert not sdda


def main():
    save_and_load_int()
    ya.ynab.gui_client.load_gui()
    ya.test.restore_test_data.rename_and_close()
    ya.test.restore_test_data.add_new_account()
    ya.utils.gui.quit()
    ya.assistant.Assistant.load_ynab_data()
    annotated = save_and_load_anotated_transactions()
    upload_to_new_account(annotated)
    time.sleep(3)
    download_and_compare(annotated)
    ya.utils.log_info('PASS')


if __name__ == '__main__':
    main()
