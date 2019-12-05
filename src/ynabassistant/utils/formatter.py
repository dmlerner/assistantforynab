import ynabassistant as ya
from copy import deepcopy


class Field:
    def __init__(self, name, value, formatter):
        self.name = name
        self.value = value
        self.formatter = formatter
        self.formatted = value is not None and formatter(value) or ''
        assert isinstance(self.formatted, str)
        self.width = None

    def __str__(self):
        self.formatted = self.formatter(self.value)
        self.width = self.width or len(self.formatted)
        return ('%-' + str(self.width) + 's') % self.formatted

    def __repr__(self):
        return str(vars(self))

    @staticmethod
    def make_fields(values_by_name, formatter=str):
        return [Field(name, value, formatter) for (name, value) in values_by_name.items()]


class Record:
    def __init__(self, fields, separator=' | '):
        self.fields = fields
        self.separator = separator

    def format(self, width_by_name):
        for f in self.fields:
            f.width = width_by_name[f.name]
        # return self.separator.join(map(str, self.fields))

    def __str__(self):
        return self.separator.join(map(str, self.fields))
        # width_by_name = {f.name: f.width for f in self.fields}
        # return self.format(width_by_name)


class Table:
    def __init__(self, records, title='', separator='\n'):
        self.records = records
        self.title = title
        self.separator = separator

    def sum(self, field_groups):
        s = deepcopy(self.records[0])
        assert isinstance(s.fields[0].value, str)
        s.fields[0].value = 'TOTAL'
        for f in s.fields:
            if type(f.value) in (int, float):
                f.value = sum(f.value for f in field_groups[f.name])
                f.formatted = f.formatter(f.value)
        return s

    def __str__(self):
        field_groups = ya.utils.group_by(sum((r.fields for r in self.records), []), lambda f: f.name)
        sum_record = self.sum(field_groups)
        width_by_name = {name: max(map(len, (name,) + tuple(f.formatted for f in fields)))
                         for (name, fields) in field_groups.items()}
        for f in sum_record.fields:
            width_by_name[f.name] = max(width_by_name[f.name], len(f.formatted))
        for r in self.records:
            r.format(width_by_name)
        sum_record.format(width_by_name)

        title_record = deepcopy(self.records[0])  # TODO: will tox hate me
        for f in title_record.fields:
            f.value = f.name
            f.formatter = lambda x: x
        bar = '*' * (sum(width_by_name.values()) + (len(width_by_name) - 1) * len(title_record.separator))
        title = self.title, bar, str(title_record), bar
        data = tuple(map(str, self.records))
        total = (bar, str(sum_record), bar)
        return self.separator.join(title + data + total)


class TableGroup:
    def __init__(self, tables, title='', separator='\n'):
        self.tables = tables
        self.title = title
        self.separator = separator

    def __str__(self):
        return self.separator.join((self.title,), map(str, self.tables))
