import ynabassistant as ya


class Budgeter:
    def __init__(self, *p):
        self.priorities = p

    def budget(self):
        ''' Fund high priority categories by withdrawing from low priority categories '''
        important = iter(self.priorities)
        unimportant = reversed(self.priorities)
        sink = next(important)
        source = next(unimportant)
        #ya.utils.debug()
        while source is not sink:
            ya.utils.log_info(source, sink)
            need = sink.total_need()
            ya.utils.log_info('need', need)
            if ya.utils.equalish(need, 0):
                sink = next(important)
                ya.utils.log_info('new sink', sink)
            available = source.total_available()
            ya.utils.log_info('available', available)
            if available <= 0:
                source = next(unimportant)
                ya.utils.log_info('new source', source)
            use = min(available, need)
            ya.utils.log_info('use', use)
            before = source.total_available() + sink.total_available()
            ya.utils.log_info('before', before)
            ya.utils.log_info('source before distribute', source)
            source.distribute(-use)
            ya.utils.log_info('source after distribute', source)
            ya.utils.log_info('sink before distribute', sink)
            sink.distribute(use)
            ya.utils.log_info('sink after distribute', sink)
            after = source.total_available() + sink.total_available()
            ya.utils.log_info('after', after)
            assert ya.utils.equalish(after, before, -1)

    def budget2(self):
        unimportant = list(reversed(self.priorities))
        for p1, p2 in zip(unimportant, unimportant[1:]):
            before = p1.total_available() + p2.total_available()
            amount = p1.total_available()
            ya.utils.log_info('moving', amount)
            ya.utils.log_info(p1, p2)
            p1.distribute(-amount)
            p2.distribute(amount)
            ya.utils.log_info('moved')
            ya.utils.log_info(p1, p2)
            after = p1.total_available() + p2.total_available()
            assert ya.utils.equalish(after, before, -1)

    def confirm(self):
        pass

    def update_ynab(self):
        categories = {g.category.name: g.category for p in self.priorities for g in p.goals}
        ya.utils.log_info("Updating %s categories" % len(categories))
        ya.ynab.api_client.update_categories(categories)  # TODO: queue via ynab.ynab

    def __repr__(self):
        out = ['%s:\n%s'%(i, str(self.priorities[i])) for i in range(len(self.priorities))]
        return '\n'.join(out)
