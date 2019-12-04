import ynabassistant as ya
import ynab_api


def test():
    # ya.Assistant.download_ynab(categories=True)
    groups = ya.backup.local.load_before(ynab_api.CategoryGroupWithCategories)
    categories = [c for g in groups for c in g.categories]
    ya.Assistant.categories = categories

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
    p.distribute()
    a.adjust_budget(-200)
    b.adjust_budget(-200)
    p.distribute()
    ya.utils.log_info(p)

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
    p2.distribute()
    d.adjust_budget(+200)
    p2.distribute()
    ya.utils.log_info(p2)
    ya.utils.log_info('...')

    bud = ya.budgeter.Budgeter(p, p2)
    bud.budget()
    ya.utils.log_info(bud)
    # ya.utils.debug()
    # bud.update_ynab()


# ya.Assistant.download_ynab(categories=True)
groups = ya.backup.local.load_before(ynab_api.CategoryGroupWithCategories)
categories = [c for g in groups for c in g.categories]
ya.Assistant.categories = categories
goals = list(filter(lambda g: g.category.name != 'Miscasdf', map(ya.budgeter.Goal, categories)))
goals.sort(key=lambda g: g.category.name)
assert all(g.is_timed() ^ g.is_static() ^ (not g.is_goal()) for g in goals)

timed = list(filter(lambda g: g.is_timed(), goals))
static = list(filter(lambda g: g.is_static(), goals))
nongoals = list(filter(lambda g: not g.is_goal(), goals))
names = ya.utils.by(goals, lambda g: g.category.name.lower())
ya.utils.log_info(*((g.category.name, g.days_remaining(), g.category.goal_type) for g in goals))

ya.utils.log_info('timed: ', *timed)
ya.utils.log_info('static: ', *static)
ya.utils.log_info('nongoals: ', *nongoals)

visa = [g for g in goals if 'BoA Visa' in g.category.name].pop()
buf = [g for g in goals if 'Buffer' in g.category.name].pop()
ho = [g for g in goals if 'Housekeeping' in g.category.name].pop()
ya.utils.log_info(visa, buf, ho)


def get(x):
    return [names[name.lower().strip()] for name in x.split(',')]


p0 = ya.budgeter.Priority(get('irs, interest & fees'))
p1 = ya.budgeter.Priority(get('digital subscription, electric, groceries, phone, renter\'s insurance'))
p2 = ya.budgeter.Priority(get('housekeeping, xiaolu'))
p3 = ya.budgeter.Priority(get('boa visa 5071'))
p4 = ya.budgeter.Priority(nongoals)

bud = ya.budgeter.Budgeter(p0, p1, p2, p3, p4)
ps = bud.priorities


def f():
    return [(p.total_available(), p.total_need()) for p in ps]


def g():
    return f(), sum(a[0] for a in f()), sum(a[1] for a in f())


g0 = g()
ya.utils.log_info(bud)
print(g0)
bud.budget3()
#ya.utils.log_info(bud)
#print(g0)
#print(g())
