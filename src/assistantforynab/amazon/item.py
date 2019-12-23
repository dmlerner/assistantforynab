from ynabassistant.utils import utils
from . import parse_date, parse_money


class Item:
    ''' Contains all fields for an item as downloaded in the csv '''

    def __init__(self, d):
        self._parent_dict = d
        self.id = d['Order ID']

        self.order_date = parse_date(d['Order Date'])
        self.item_total = parse_money(d['Item Total'])
        self.title = d['Title']

        self.category = d['Category']
        self.seller = d['Seller']
        self.quantity = d['Quantity']

    def __str__(self):
        str_fields = utils.format_date(self.order_date), \
            utils.format_money(self.item_total), self.title
        return ' | '.join(map(str, str_fields))
