import ynabassistant as ya


class Order:
    ''' Contains all fields for an order as downloaded in the csv '''

    def __init__(self, d):
        self._parent_dict = d
        self.order_date = ya.amazon.utils.parse_date(d['order_date'])
        self.order_id = d['order_id']
        self.shipment_date = ya.amazon.utils.parse_date(d['shipment_date'])
        self.total_charged = ya.amazon.utils.parse_money(d['total_charged'])

    def __repr__(self):
        fields = ya.amazon.utils.date_format(self.order_date),\
            ya.utils.format_money(self.total_charged), self.order_id
        return ' | '.join(map(str, fields))

    '''
    I think I'm not using this...
    def __lt__(self, other):
        assert isinstance(other, ya.amazon.Item)
        return self.order_date < other.order_date

    def __in__(self, order):
        assert isinstance(order, ya.order.Order)
        return self.order_id == order_order_id
    '''

    # used to combine orders that shipped separately
    def __add__(self, other):
        assert isinstance(other, Order)
        assert other.order_id == self.order_id
        combined_dict = self._parent_dict.copy()
        other_dict = other._parent_dict.copy()
        for k in other.__dict__:
            if other_dict[k] == combined_dict[k]:
                continue
            if '$' in other_dict[k] and '$' in combined_dict[k]:
                combined_dict[k] = '$' + str(parse_money(other_dict[k]) + parse_money(combined_dict[k]))
            else:
                combined_dict[k] += ', ' + other_dict[k]
        return Order(combined_dict)
