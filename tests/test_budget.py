import ynabassistant as ya


def main():
    ya.Assistant.download_ynab(categories=True)
    goals = list(filter(lambda g: g.days_remaining(),
                        map(ya.budgeter.Goal,
                            ya.Assistant.categories)))
    p = ya.budgeter.Priority(goals[:3], (1, 1, 2))
    a, b, c = p.goals
    a.name = 'a'
    a.target_month = ya.ynab.utils.first_of_coming_month()
    b.name = 'b'
    b.target_month = ya.ynab.utils.first_of_coming_month() + 10 * ya.utils.one_day
    c.name = 'c'
    c.target_month = ya.ynab.utils.first_of_coming_month() + 30 * ya.utils.one_day
    for C in p.goals:
        C.adjust_budget(C.amount_remaining())
    ya.utils.log_debug(p.distribute())
    a.adjust_budget(-200)
    b.adjust_budget(-200)
    p.distribute()
    ya.utils.log_debug(p)

    p2 = ya.budgeter.Priority(goals[3:6], (1, 1, 2))
    d, e, f = p2.goals
    d.name = 'd'
    d.target_month = ya.ynab.utils.first_of_coming_month()
    e.name = 'e'
    e.target_month = ya.ynab.utils.first_of_coming_month() + 10 * ya.utils.one_day
    f.name = 'f'
    f.target_month = ya.ynab.utils.first_of_coming_month() + 30 * ya.utils.one_day
    for C in p2.goals:
        C.adjust_budget(C.amount_remaining())
    ya.utils.log_debug(p2.distribute())
    d.adjust_budget(+200)
    p2.distribute()
    ya.utils.log_debug(p2)
    ya.utils.log_debug('...')

    bud = ya.budgeter.Budgeter(p, p2)
    bud.budget()
    ya.utils.log_debug(bud)
    #ya.utils.debug()
    bud.update_ynab()


if __name__ == '__main__':
    main()
