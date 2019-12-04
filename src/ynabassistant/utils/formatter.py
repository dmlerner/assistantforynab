import ynabassistant as ya


class Field:
    def __init__(self, name, value, formatter):
        self.name = name
        self.formatted = value is not None and formatter(value) or ''
        assert isinstance(self.formatted, str)
        self.width = None

    def __str__(self):
        self.width = self.width or len(self.formatted)
        return ('%' + str(self.width) + 's') % self.formatted

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

    def __str__(self):
        field_groups = ya.utils.group_by(sum((r.fields for r in self.records), []), lambda f: f.name)
        width_by_name = {name: max(map(len, (name,) + tuple(f.formatted for f in fields)))
                         for (name, fields) in field_groups.items()}
        ya.utils.log_info('table.str', width_by_name)
        for r in self.records:
            r.format(width_by_name)
        return self.separator.join((self.title,) + tuple(map(str, self.records)))


class TableGroup:
    def __init__(self, tables, title='', separator='\n'):
        self.tables = tables
        self.title = title
        self.separator = separator

    def __str__(self):
        return self.separator.join((self.title,), map(str, self.tables))
