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

budget_id = '7b027e9b-4ed8-495e-97bd-f0339357adf0'
account_name = 'Chase Amazon'
api_key = 'd8603f5c0e704f36bd0774e162c1651c8416974b181ff0dc45de427f75bbb20e'

fail_on_ambiguous_transaction = False
' NOTE: you probalby want to make a category named as below '
default_category = 'ERROR'
close_browser_on_finish = False

' Always redownload csvs '
force_download_amazon = False

' TODO: variable controlling if transactions stay checked in the UI when done; currently they do '
' TODO: actually use log levels '
' TODO: classes instead of all these dictionaries '
' TODO: call get transactions via official ruby api '
' TODO: configurable amazon download length; currently 30 days '
