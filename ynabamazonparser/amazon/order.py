import datetime
import dataclasses
from ynabamazonparser import amazon


@dataclasses.dataclass
class Order:
    ''' Contains all fields for an order as downloaded in the csv '''
    _order_date: str
    order_id: str
    payment_instrument_type: str
    website: str
    purchase_order_number: str
    ordering_customer_email: str
    shipment_date: str
    shipping_address_name: str
    shipping_address_street_1: str
    shipping_address_street_2: str
    shipping_address_city: str
    shipping_address_state: str
    shipping_address_zip: str
    order_status: str
    carrier_name_and_tracking_number: str
    subtotal: str
    shipping_charge: str
    tax_before_promotions: str
    total_promotions: str
    tax_charged: str
    _total_charged: str
    buyer_name: str
    group_name: str

    def from_dict(d):
        return Order(*d.values())

    @property
    def order_date(self):
        return to_datetime(self._order_date)

    @property
    def total_charged(self):
        return to_float(self._total_charged)

    def __repr__(self):
        fields = self.order_id, self._order_date, self._total_charged
        return ' | '.join(map(str, fields))

    def __lt__(self, other):
        assert isinstance(other, amazon.Item)
        return self.order_date < other.order_date

    def __in__(self, order):
        assert isinstance(order, order.Order)
        return self._order_id == order._order_id

    def __add__(self, other):
        assert isinstance(other, Order)
        assert other.order_id == self.order_id
        combined_dict = self.__dict__.copy()
        other_dict = other.__dict__.copy()
        for k in other.__dict__:
            if other_dict[k] == combined_dict[k]:
                continue
            if '$' in other_dict[k] and '$' in combined_dict[k]:
                combined_dict[k] = '$' + str(to_float(other_dict[k]) + to_float(combined_dict[k]))
            else:
                combined_dict[k] += ', ' + other_dict[k]
        return Order.from_dict(combined_dict)


def to_float(price):
    ''' $123.45::str -> 123.45::float '''
    return float(price[1:])


date_format = '%m/%d/%y'


def to_datetime(d):
    return datetime.datetime.strptime(d, date_format)
