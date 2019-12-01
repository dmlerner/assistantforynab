import ynabassistant as ya
c = ya.ynab.api_client.Client()
ts = c.get_all_transactions()[:3]
ya.utils.debug_assert(ts)
c.update_transactions(ts)
c.create_transactions(ts)
cs = c.get_categories()
ya.utils.debug_assert(cs)
