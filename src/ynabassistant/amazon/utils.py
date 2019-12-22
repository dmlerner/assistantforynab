from ynabassistant.utils import utils


def parse_money(price):
    assert isinstance(price, str)
    if not price or price[0] != '$':
        return None
    return float(price[1:])


date_format = '%m/%d/%y'


def parse_date(d):
    return utils.parse_date(d, date_format)


def format_date(d):
    return utils.format_date(d, date_format)
