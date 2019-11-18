import ynabamazonparser as yap


def parse_money(price):
    assert isinstance(price, int)
    return price / 1000

def to_milliunits(p):
    return int(p*1000)


date_format = '%Y-%m-%d'


def parse_date(d):
    return yap.utils.parse_date(d, date_format)


def format_date(d):
    return yap.utils.format_date(d, date_format)
