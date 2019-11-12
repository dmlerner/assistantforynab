import datetime
import os
import sys
import pdb
import time

start_time = datetime.datetime.now()
log_verbosity = 0
print_verbosity = 0

home = os.path.expanduser('~')

' TODO clean up; wsl paths are confusing '
chrome_data_dir = os.path.join(home, '\\AppData\\Local\\Google\\Chrome\\User Data\\Default')
' NOTE: must have the chromedriver named chromedriver (not chromedriver.exe), somewhere in your PATH '

downloads_path = os.path.join(home, 'Downloads')
script_path = os.getcwd()
log_path = os.path.join(script_path, 'log')
data_path = os.path.join(script_path, 'data')
for p in log_path, data_path:
    if not os.path.exists(p):
        os.mkdir(p)

' just go to your ynab; the url is app.youneedabudget.com/BUDGET_ID/budget '
' looks like 8-4-4-4-12 alpha numerics '
budget_id = ' your budget id here '

' the name of the one account to check for amazon transactions '
' TODO: work with multiple acounts '
account_name = 'Chase Amazon'

' api.youneedabudget.com '
' you want a "personal access token" '
' TODO: oauth '
api_key = 'your personal access token here'

fail_on_ambiguous_transaction = False
' NOTE: you probalby want to make a category named as below '
default_category = 'ERROR'
close_browser_on_finish = False

' if true, Always redownload csvs '
force_download_amazon = False

' TODO: variable controlling if transactions stay checked in the UI when done; currently they do '
' TODO: actually use log levels '
' TODO: classes instead of all these dictionaries '
' TODO: call get transactions via official ruby api '
' TODO: configurable amazon download length; currently 30 days '
