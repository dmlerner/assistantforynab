import ynab_api

from ynabassistant.utils import utils
import ynabassistant as ya
import ynabassistant.assistant.assistant
import ynabassistant.ynab.utils
# ynabassistant.assistant.assistant import Assistant
from ynabassistant import ynab, settings


def annotate(t, order, items):
    utils.log_debug('annotate', t, order, items)
    t.date = order.order_date
    if len(items) == 1:
        annotate_with_item(t, items[0])
        t.memo += ' ' + order.id
    else:
        t.memo = order.id
        t.subtransactions = [ynab_api.SubTransaction(
            local_vars_configuration=ynab.no_check_configuration)
            for i in items]
        for i, s in zip(items, t.subtransactions):
            annotate_with_item(s, i)
        assert len(t.subtransactions) == len(items)
    utils.log_info(t)


def annotate_with_item(st, i):
    utils.log_debug('annotate_with_item')
    ynab.utils.type_assert_st(st)

    # ynab_api will create payee if needed when id is null
    # payee_name doesn't actually exist on subtransaction
    # but rest_client ignores subtransactions
    # and it's useful to gui_client
    st.payee_name = get_payee_name(i)
    st.payee_id = None

    # category_name exists on transaction, but not savetransaction
    # similarly, ignored by rest_client but used by gui_client
    st.category_name = get_category_name(i)
    category = ya.assistant.Assistant.accounts.by_name(st.category_name)
    st.category_id = category.id if category else None

    st.memo = i.title
    st.amount = ynab.utils.to_milliunits(-i.item_total)


def get_category_name(item):
    # TODO: business logic?
    # TODO: what if category_name exists in multiple category groups
    name = settings.default_category
    return name


def get_payee_name(item):
    return item.seller


@utils.listy
def get_eligible_transactions(transactions):
    utils.log_debug('get_eligible_transactions')
    predicates = newer_than, has_blank_or_WIP_memo, matches_account
    eligible = utils.multi_filter(predicates, transactions)
    utils.log_info('Found %s transactions to attempt to match with Amazon orders' % len(eligible))
    return utils.by(eligible, lambda t: t.id)


def has_blank_memo(t):
    return not t.memo


def has_blank_or_WIP_memo(t):
    return has_blank_memo(t) or ya.ynab.utils.starts_with_id(t.memo)


def matches_account(t):
    return t.account_name.lower() == settings.account_name.lower()  # TODO: remove explicit dependence on settings


def newer_than(t, days_ago=30):
    return utils.newer_than(t.date, days_ago)
