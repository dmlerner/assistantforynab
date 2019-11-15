import datetime
import dataclasses


@dataclasses.dataclass
class Item:
    ''' Contains all fields for an item as downloaded in the csv '''
    _order_date: str
    order_id: str
    title: str
    category: str
    asin_isbn: str
    unspsc_code: str
    website: str
    release_date: str
    condition: str
    seller: str
    seller_credentials: str
    list_price_per_unit: str
    purchase_price_per_unit: str
    quantity: str
    payment_instrument_type: str
    purchase_order_number: str
    po_line_number: str
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
    item_subtotal: str
    item_subtotal_tax: str
    _item_total: str
    tax_exemption_applied: str
    tax_exemption_type: str
    exemption_opt_out: str
    buyer_name: str
    currency: str
    group_name: str

    def from_dict(d):
        return Item(*d.values())

    @property
    def order_date(self):
        return to_datetime(self._order_date)

    @property
    def item_total(self):
        return to_float(self._item_total)

    def __str__(self):
        str_fields = self.title, self._order_date, self._item_total
        return 'Item: ' + ' | '.join(map(str, str_fields))

    def __lt__(self, other):
        assert type(other) is Item
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
