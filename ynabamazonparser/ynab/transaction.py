def datetime_from_ynab_date(d, fmt='%Y-%m-%d'):
    return datetime.datetime.strptime(d, fmt)
def float_from_ynab_price(p):
    try:
        return abs(p/1000)
    except:
        return None
