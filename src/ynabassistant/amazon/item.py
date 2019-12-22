from ynabassistant.utils import utils
import ynabassistant as ya
import ynabassistant.amazon.utils


class Item:
    ''' Contains all fields for an item as downloaded in the csv '''

    def __init__(self, d):
        self._parent_dict = d
        self.id = d['Order ID']

        self.order_date = ya.amazon.utils.parse_date(d['Order Date'])
        self.item_total = ya.amazon.utils.parse_money(d['Item Total'])
        self.title = d['Title']

        self.category = d['Category']
        self.seller = d['Seller']
        self.quantity = d['Quantity']

    def __repr__(self):
        str_fields = utils.format_date(self.order_date), \
            utils.format_money(self.item_total), self.title
        return ' | '.join(map(str, str_fields))
