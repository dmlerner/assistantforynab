import ynabamazonparser as yap
import datetime


def main():
    '''
    a = yap.assistant.Assistant()
    a.load_amazon_data()
    a.load_ynab_data()
    a.update_amazon_transactions()
    a.update_ynab()
    yap.utils.log_info('Success')
    '''
    categories = yap.ynab.api_client.get_categories()
    cat = [c for c in categories if c.goal_type]
    p = yap.assistant.budgeter.Priority(*cat[:3])

    b = yap.assistant.budgeter.Budgeter(p, p2)


if __name__ == '__main__':
    categories = yap.ynab.api_client.get_categories()
    cat = [c for c in categories.values() if c.goal_days_remaining()]
    p = yap.assistant.budgeter.Priority(cat[:3], (1, 1, 2))
    a,b,c=p.categories
    a.name = 'a'
    one_day = datetime.timedelta(1)
    a.goal_target_month = yap.ynab.utils.first_of_coming_month()
    b.name = 'b'
    b.goal_target_month = yap.ynab.utils.first_of_coming_month() + 10*one_day
    c.name = 'c'
    c.goal_target_month = yap.ynab.utils.first_of_coming_month() + 30*one_day
    for C in p.categories:
        C.adjust_budget(C.goal_amount_remaining())
    yap.utils.log_debug(p.distribute())
    a.adjust_budget(-200)
    b.adjust_budget(-200)
    p.distribute()
    yap.utils.log_debug(p)

    p2 = yap.assistant.budgeter.Priority(cat[3:6], (1, 1, 2))
    d,e,f=p2.categories
    d.name = 'd'
    d.goal_target_month = yap.ynab.utils.first_of_coming_month()
    e.name = 'e'
    e.goal_target_month = yap.ynab.utils.first_of_coming_month() + 10*one_day
    f.name = 'f'
    f.goal_target_month = yap.ynab.utils.first_of_coming_month() + 30*one_day
    for C in p2.categories:
        C.adjust_budget(C.goal_amount_remaining())
    yap.utils.log_debug(p2.distribute())
    d.adjust_budget(+200)
    p2.distribute()
    yap.utils.log_debug(p2)
    yap.utils.log_debug('...')

    bud = yap.assistant.budgeter.Budgeter(p, p2)
    bud.budget()
    yap.utils.log_debug(bud)
