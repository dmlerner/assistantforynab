import assistantforynab as afy


def test():
    pass


afy.Assistant.load_ynab(categories=True, accounts=True, local=True)

goals = list(filter(lambda g: g.category.name != 'Miscasdf', map(afy.budgeter.Goal, afy.Assistant.categories)))
goals.sort(key=lambda g: g.category.name)
assert all(g.is_timed() ^ g.is_static() ^ (not g.is_goal()) for g in goals)

timed = list(filter(lambda g: g.is_timed(), goals))
static = list(filter(lambda g: g.is_static(), goals))
nongoals = list(filter(lambda g: not g.is_goal(), goals))
names = afy.utils.by(goals, lambda g: g.category.name.lower())
afy.utils.log_info(*((g.category.name, g.days_remaining(), g.category.goal_type) for g in goals))

afy.utils.log_info('timed: ', *timed)
afy.utils.log_info('static: ', *static)
afy.utils.log_info('nongoals: ', *nongoals)

visa = [g for g in goals if 'BoA Visa' in g.category.name].pop()
buf = [g for g in goals if 'Buffer' in g.category.name].pop()
ho = [g for g in goals if 'Housekeeping' in g.category.name].pop()
afy.utils.log_info(visa, buf, ho)


def get(x):
    return [names[name.lower().strip()] for name in x.split(',')]


#    p0, p1, p2, p3, p4, p5 =\
p0, p1 = priorities =\
    [afy.budgeter.Priority(get(x)) for x in
     (
        #'boa visa 5071',
        #'chase 1.5%, chase amazon',
        'irs, interest & fees',
        'digital subscription, electric, groceries, phone, renter\'s insurance',
        #'housekeeping, xiaolu',
    )]  # + [afy.budgeter.Priority(nongoals)]

bud = afy.budgeter.Budgeter(*priorities)
afy.utils.debug()
bud.budget3()
afy.utils.log_info(bud)


if __name__ == '__main__':
    test()
