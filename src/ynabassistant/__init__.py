from . import settings, utils, assistant, backup, amazon, ynab#, budgeter
from .assistant import Assistant

if settings.get('budget_id') == "7b027e9b-4ed8-495e-97bd-f0339357adf0":
    choice = input('You sure you want to use the real budget man? [y/N]')
    if choice != 'y':
        import sys
        sys.exit()
