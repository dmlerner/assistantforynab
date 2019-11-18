import ynabamazonparser as yap


class Item:
    ''' Contains all fields for an item as downloaded in the csv '''

    def __init__(self, d):
        self._parent_fields = d
        self.order_id = d['order_id']

        self.order_date = yap.amazon.utils.parse_date(d['order_date'])
        self.item_total = yap.amazon.utils.parse_money(d['item_total'])
        self.title = d['title']

        self.category = d['category']
        self.seller = d['seller']
        self.quantity = d['quantity']

    def __repr__(self):
        str_fields = yap.amazon.utils.format_date(self.order_date), \
            yap.utils.format_money(self.item_total), self.title
        return ' | '.join(map(str, str_fields))
