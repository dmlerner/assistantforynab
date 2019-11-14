import datetime
import dataclasses

@dataclasses.dataclass
class Item:
    ''' Contains all fields for an item as downloaded in the csv '''
    _order_date: str
    _order_id: str
    _title: str
    _category: str
    _asin_isbn: str
    _unspsc_code: str
    _website: str
    _release_date: str
    _condition: str
    _seller: str
    _seller_credentials: str
    _list_price_per_unit: str
    _purchase_price_per_unit: str
    _quantity: str
    _payment_instrument_type: str
    _purchase_order_number: str
    _po_line_number: str
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
    _item_subtotal: str
    _item_subtotal_tax: str
    _item_total: str
    _tax_exemption_applied: str
    _tax_exemption_type: str
    _exemption_opt_out: str
    _buyer_name: str
    _currency: str
    _group_name: str

    @property
    def title(self):
        return self._title

    @property
    def order_date(self):
        return to_datetime(self._order_date)

    @property
    def item_total(self):
        return to_float(self._item_total)

    def __str__(self):
        return 'Item: ' + ' | '.join(map(str, (self._title, self._order_date, self._item_total)))

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
