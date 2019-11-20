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


if __name__ == '__main__':
    categories = yap.ynab.api_client.get_categories()
    cat = [c for c in categories.values() if c.goal_days_remaining() ]
    p = yap.assistant.budgeter.Priority(*cat[:3])
    a,b,c=p.categories
    a.name = 'a'
    one_day = datetime.timedelta(1)
    a.goal_target_month = yap.ynab.utils.first_of_coming_month()
    b.name = 'b'
    b.goal_target_month = yap.ynab.utils.first_of_coming_month() + 30*one_day
    c.name = 'c'
    c.goal_target_month = yap.ynab.utils.first_of_coming_month() + 3000*one_day
    for C in p.categories:
        C.adjust_budget(C.goal_amount_remaining())
    yap.utils.log_debug(p.redistribute())
    a.adjust_budget(-2)
    b.adjust_budget(-2)
    p.redistribute()
    #p.distribute(1)
