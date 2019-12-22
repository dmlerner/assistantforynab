import utils


def diff_transactions(ts1, ts2):
    d12, d21 = diff(ts1, ts2, to_tuple)
    utils.log_debug(*d12)
    utils.log_debug(*d21)
    ds12, ds21 = diff([s for t in ts1 for s in t.subtransactions],
                      [s for t in ts2 for s in t.subtransactions], sub_to_tuple)
    utils.log_debug(*ds12)
    utils.log_debug(*ds21)
    return d12, d21, ds12, ds21


def to_tuple(t):
    return t.amount, t.approved, t.category_id, t.category_name, t.cleared, t.date, \
        t.deleted, t.flag_color, t.memo, t.payee_id, t.payee_name, t.transfer_account_id


def sub_to_tuple(s):
    return s.amount, s.category_id, s.deleted, s.memo, s.payee_id, s.transfer_account_id


def diff(ts1, ts2, tupler):
    tuple_ts1 = set(map(tupler, ts1))
    tuple_ts2 = set(map(tupler, ts2))
    return tuple_ts1 - tuple_ts2, tuple_ts2 - tuple_ts1
