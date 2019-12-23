from assistantforynab.utils import utils


def parse_money(price):
    assert isinstance(price, str)
    if not price or price[0] != '$':
        return None
    return float(price[1:])


date_format = '%m/%d/%y'


def parse_date(d):
    # TODO: less hacky solution
    # if multiple shipment dates in one order, order.__add__ will trigger this
    d = d.split(',')[0]

    return utils.parse_date(d, date_format)


def format_date(d):
    return utils.format_date(d, date_format)
