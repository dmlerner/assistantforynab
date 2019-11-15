import datetime
import dataclasses
from ynabamazonparser import amazon


@dataclasses.dataclass
class Order:
    ''' Contains all fields for an order as downloaded in the csv '''
    _order_date: str
    _order_id: str
    _payment_instrument_type: str
    _website: str
    _purchase_order_number: str
    _ordering_customer_email: str
    _shipment_date: str
    _shipping_address_name: str
    _shipping_address_street_1: str
    _shipping_address_street_2: str
    _shipping_address_city: str
    _shipping_address_state: str
    _shipping_address_zip: str
    _order_status: str
    _carrier_name_and_tracking_number: str
    _subtotal: str
    _shipping_charge: str
    _tax_before_promotions: str
    _total_promotions: str
    _tax_charged: str
    _total_charged: str
    _buyer_name: str
    _group_name: str

    @property
    def order_date(self):
        return to_datetime(self._order_date)

    @property
    def item_total(self):
        return to_float(self._item_total)

    def __str__(self):
        str_fields = self._title, self._order_date, self._item_total
        return 'Item: ' + ' | '.join(map(str, str_fields))

    def __lt__(self, other):
        assert type(other) is amazon.Item
        return self.order_date < other.order_date

    def __in__(self, order):
        assert type(order) is order.Order
        return self._order_id == order._order_id


def to_float(price):
    ''' $123.45::str -> 123.45::float '''
    return float(price[1:])


date_format = '%m/%d/%y'


def to_datetime(d):
    return datetime.datetime.strptime(d, date_format)
