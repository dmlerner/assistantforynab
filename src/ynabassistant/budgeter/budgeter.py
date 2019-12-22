import utils
import ynab


class Budgeter:
    def __init__(self, *p):
        self.priorities = p

    def budget(self):
        ''' Fund high priority categories by withdrawing from low priority categories '''
        important = iter(self.priorities)
        unimportant = reversed(self.priorities)
        sink = next(important)
        source = next(unimportant)
        # utils.debug()
        while source is not sink:
            utils.log_info(source, sink)
            need = sink.total_need()
            utils.log_info('need', need)
            if utils.equalish(need, 0):
                sink = next(important)
                utils.log_info('new sink', sink)
            available = source.total_available()
            utils.log_info('available', available)
            if available <= 0:
                source = next(unimportant)
                utils.log_info('new source', source)
            use = min(available, need)
            utils.log_info('use', use)
            before = source.total_available() + sink.total_available()
            utils.log_info('before', before)
            utils.log_info('source before distribute', source)
            source.distribute(-use)
            utils.log_info('source after distribute', source)
            utils.log_info('sink before distribute', sink)
            sink.distribute(use)
            utils.log_info('sink after distribute', sink)
            after = source.total_available() + sink.total_available()
            utils.log_info('after', after)
            assert utils.equalish(after, before, -1)

    def budget2(self):
        unimportant = list(reversed(self.priorities))
        for p1, p2 in zip(unimportant, unimportant[1:]):
            before = p1.total_available() + p2.total_available()
            amount = p1.total_available()
            utils.log_info('moving', amount)
            utils.log_info(p1, p2)
            p1.distribute(-amount)
            p2.distribute(amount)
            utils.log_info('moved')
            utils.log_info(p1, p2)
            after = p1.total_available() + p2.total_available()
            assert utils.equalish(after, before, -1)

    def budget3(self):
        utils.debug()
        avail = sum(p.withdraw_all() for p in self.priorities)
        self.priorities[0].distribute(avail)
        surplus = self.priorities[0].withdraw_surplus()
        for p in self.priorities[1:]:
            p.distribute(surplus)
            surplus = p.withdraw_surplus()
        self.priorities[0].distribute(surplus)
        self.priorities[0].distribute(sum(p.withdraw_surplus() for p in self.priorities[1:]))

    def confirm(self):
        pass

    def update_ynab(self):
        categories = {g.category.name: g.category for p in self.priorities for g in p.goals}
        utils.log_info("Updating %s categories" % len(categories))
        ynab.api_client.update_categories(categories)  # TODO: queue via ynab.ynab

    def __repr__(self):
        out = ['%s:%s\n' % (i, str(self.priorities[i])) for i in range(len(self.priorities))]
        return '\n'.join(out)
