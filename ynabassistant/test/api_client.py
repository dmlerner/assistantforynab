import ynabassistant as ya
c = ya.ynab.api_client.Client()
trans = list(c.get_all_transactions().values())[:3]
assert trans
c.update_transactions(trans)
c.create_transactions(trans)
cats = c.get_categories()
assert cats

