import ynabassistant as ya


def parse_money(price):
    assert type(price) is str
    if not price or price[0] != '$':
        return None
    return float(price[1:])


date_format = '%m/%d/%y'


def parse_date(d):
    return ya.utils.parse_date(d, date_format)


def format_date(d):
    return ya.utils.format_date(d, date_format)
