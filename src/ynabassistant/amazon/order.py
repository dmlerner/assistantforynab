from ynabassistant.utils import utils
import ynabassistant as ya
import ynabassistant.amazon.utils


class Order:
    ''' Contains all fields for an order as downloaded in the csv '''

    def __init__(self, d):
        self._parent_dict = d
        utils.log_debug(d)
        self.order_date = ya.amazon.utils.parse_date(d['Order Date'])
        self.id = d['Order ID']
        self.shipment_date = ya.amazon.utils.parse_date(d['Shipment Date'])
        self.total_charged = ya.amazon.utils.parse_money(d['Total Charged'])

    def __repr__(self):
        fields = ya.amazon.utils.format_date(self.order_date),\
            utils.format_money(self.total_charged), self.id
        return ' | '.join(map(str, fields))

    # used to combine orders that shipped separately
    def __add__(self, other):
        utils.log_debug(self, other)
        utils.log_debug(self.__dict__, other.__dict__)
        assert isinstance(other, Order)
        assert other.id == self.id
        utils.log_debug(self.__dict__.keys(), other.__dict__.keys())
        assert set(self.__dict__.keys()) == set(other.__dict__.keys())
        utils.log_debug(self._parent_dict.keys(), other._parent_dict.keys())
        assert set(self._parent_dict.keys()) == set(other._parent_dict.keys())
        combined_dict = self._parent_dict.copy()
        other_dict = other._parent_dict.copy()
        for k in combined_dict:
            if other_dict[k] == combined_dict[k]:
                continue
            if '$' in other_dict[k] and '$' in combined_dict[k]:
                combined_dict[k] = '$' + str(ya.amazon.utils.parse_money(other_dict[k]) +
                                             ya.amazon.utils.parse_money(combined_dict[k]))
            else:
                combined_dict[k] += ', ' + other_dict[k]
        return Order(combined_dict)
