import ynabassistant as ya
import datetime


def main():
    '''
    a = ya.assistant.Assistant()
    a.load_amazon_data()
    a.load_ynab_data()
    a.update_amazon_transactions()
    a.update_ynab()
    ya.utils.log_info('Success')
    '''
    categories = ya.ynab.api_client.get_categories()
    cat = [c for c in categories if c.goal_type]
    p = ya.assistant.budgeter.Priority(*cat[:3])

    b = ya.assistant.budgeter.Budgeter(p, p2)


if __name__ == '__main__':
    categories = ya.ynab.api_client.get_categories()
    cat = [c for c in categories.values() if c.goal_days_remaining()]
    p = ya.budgeter.Priority(cat[:3], (1, 1, 2))
    a,b,c=p.categories
    a.name = 'a'
    one_day = datetime.timedelta(1)
    a.goal_target_month = ya.ynab.utils.first_of_coming_month()
    b.name = 'b'
    b.goal_target_month = ya.ynab.utils.first_of_coming_month() + 10*one_day
    c.name = 'c'
    c.goal_target_month = ya.ynab.utils.first_of_coming_month() + 30*one_day
    for C in p.categories:
        C.adjust_budget(C.goal_amount_remaining())
    ya.utils.log_debug(p.distribute())
    a.adjust_budget(-200)
    b.adjust_budget(-200)
    p.distribute()
    ya.utils.log_debug(p)

    p2 = ya.budgeter.Priority(cat[3:6], (1, 1, 2))
    d,e,f=p2.categories
    d.name = 'd'
    d.goal_target_month = ya.ynab.utils.first_of_coming_month()
    e.name = 'e'
    e.goal_target_month = ya.ynab.utils.first_of_coming_month() + 10*one_day
    f.name = 'f'
    f.goal_target_month = ya.ynab.utils.first_of_coming_month() + 30*one_day
    for C in p2.categories:
        C.adjust_budget(C.goal_amount_remaining())
    ya.utils.log_debug(p2.distribute())
    d.adjust_budget(+200)
    p2.distribute()
    ya.utils.log_debug(p2)
    ya.utils.log_debug('...')

    bud = ya.budgeter.Budgeter(p, p2)
    bud.budget()
    ya.utils.log_debug(bud)
