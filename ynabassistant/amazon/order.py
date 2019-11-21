import ynabassistant as ya
from . import *


class Order:
    ''' Contains all fields for an order as downloaded in the csv '''

    def __init__(self, d):
        self._parent_dict = d
        ya.utils.log_debug(d)
        self.order_date = utils.parse_date(d['Order Date'])
        self.order_id = d['Order ID']
        self.shipment_date = utils.parse_date(d['Shipment Date'])
        self.total_charged = utils.parse_money(d['Total Charged'])

    def __repr__(self):
        fields = utils.format_date(self.order_date),\
            ya.utils.format_money(self.total_charged), self.order_id
        return ' | '.join(map(str, fields))

    # used to combine orders that shipped separately
    def __add__(self, other):
        ya.utils.log_debug(self, other)
        ya.utils.log_debug(self.__dict__, other.__dict__)
        assert isinstance(other, Order)
        assert other.order_id == self.order_id
        ya.utils.log_debug(self.__dict__.keys(), other.__dict__.keys())
        assert set(self.__dict__.keys()) == set(other.__dict__.keys())
        ya.utils.log_debug(self._parent_dict.keys(), other._parent_dict.keys())
        assert set(self._parent_dict.keys()) == set(other._parent_dict.keys())
        combined_dict = self._parent_dict.copy()
        other_dict = other._parent_dict.copy()
        for k in combined_dict:
            if other_dict[k] == combined_dict[k]:
                continue
            if '$' in other_dict[k] and '$' in combined_dict[k]:
                combined_dict[k] = '$' + str(utils.parse_money(other_dict[k]) + utils.parse_money(combined_dict[k]))
            else:
                combined_dict[k] += ', ' + other_dict[k]
        return Order(combined_dict)
