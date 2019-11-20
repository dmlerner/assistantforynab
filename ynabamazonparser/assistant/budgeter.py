import collections

import ynabamazonparser as yap

'''
From highest to lowest priority:
1) No budget category goes negative unless it is a credit card
2) Within a category, split new money proportional to needed rate to hit goal
3
'''
class Budgeter:
    def __init__(self):
        self.priorities = collections.defaultdict(list)

    def get_ordered_priorities(self):
        return [self.priorities[p] for p in sorted(self.priorities)]


class Priority:
    def __init__(self, *c):
        assert all(type(C)  is yap.ynab.category.Category for C in c)
        self.categories = c

    def get_total_need(self):
        yap.utils.log_debug('total need%s'% sum(c.goal_amount_remaining() for c in self.categories))
        return sum(c.goal_amount_remaining() for c in self.categories)

    def get_normalized_rates(self):
        # rates = [c.budget_rate_required() for c in self.categories]
        days = [c.goal_days_remaining() for c in self.categories]
        # each cateogry's fractional need should equal its fraction of sum(days)
        # in order ot hav equal rates
        # and fractional need is jus tanother name for normalized rate
        need = self.get_total_need()
        # need of a category should be proportional its goal days remaining
        return [d / sum(days) for d in days]

    def redistribute(self):
        '''
        Make all goals have equal budget rates required
        Return any excess
        '''
        s = str(self)
        need = self.get_total_need()
        yap.utils.log_debug('%%%%%redistribute, need='+str(need))
        if need > 0:
            rates = self.get_normalized_rates()
            for r, c in zip(rates, self.categories):
                yap.utils.log_debug('adjusting:', 'rate= %s'%r, 'cat=%s'%c, 'bal=%s'%c.balance, 'bud=%s'%c.budgeted)
                c.adjust_budget(c.goal_amount_remaining() - r * need)
                yap.utils.log_debug('adjusted:', 'rate= %s'%r, 'cat=%s'%c, 'bal=%s'%c.balance, 'bud=%s'%c.budgeted)
                #c.adjust_budget(c.goal_amount_remaining() + r * need)

            assert yap.utils.equalish(self.get_total_need(), need)
            # return 0 # this happens implicitly

        else:
        #if need <= 0:
            for c in self.categories:
                c.adjust_budget(c.goal_amount_remaining())
            assert yap.utils.equalish(self.get_total_need(), 0)
            # return -need # happens implicitly

        yap.utils.log_debug('redistributed', s, '.'*20, self)
        assert all(yap.utils.equalish(a.budget_rate_required(), b.budget_rate_required()) for (a, b) in zip(self.categories, self.categories[1:]))
        return self.get_total_need() - need

    def distribute(self, amount):
        '''
        Return any excess
        '''

        yap.utils.log_debug('%%%%%%budgeter.distribute', amount)
        excess = self.redistribute()
        s = str(self)
        yap.utils.log_debug('excess%s', excess)
        need = self.get_total_need()
        if need <= 0:
            return amount
        use = min(amount, need)
        yap.utils.log_debug('need%s'%need, 'use%s'%use)

        rates = self.get_normalized_rates()
        for r, c in zip(rates, self.categories):
            c.adjust_budget(r * use)
        assert yap.utils.equalish(self.get_total_need(), need - use)
        remaining = max(0, amount - use)
        yap.utils.log_debug('amount%s'%amount, 'use%s'%use)
        assert amount >= use # if this is true, and I think it is, no need for the above max
        yap.utils.log_debug(s, '.'*40, self)
        return remaining

    def __repr__(self):
        return '\n'.join(map(str, self.categories))


