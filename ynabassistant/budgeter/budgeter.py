import collections
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
        while source is not sink:
            need = sink.get_total_need()
            if ya.utils.equalish(need, 0):
                sink = next(important)
            available = source.get_total_available()
            if available <= 0:
                source = next(unimportant)
            use = min(available, need)
            before = source.get_total_available() + sink.get_total_available()
            source.distribute(-use)
            sink.distribute(use)
            after = source.get_total_available() + sink.get_total_available()
            assert ya.utils.equalish(after, before)

    def __repr__(self):
        return '\n'.join(map(str, self.priorities))
