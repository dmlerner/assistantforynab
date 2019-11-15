import datetime
import os
import shutil
from ynabamazonparser import utils
from ynabamazonparser.config import private_settings

start_time = datetime.datetime.now()
log_verbosity = 0
print_verbosity = 0

home = os.path.expanduser('~')

' TODO clean up; wsl paths are confusing '
chrome_data_dir = os.path.join(
    home, '\\AppData\\Local\\Google\\Chrome\\User Data\\Default')
' NOTE: must have the chromedriver named chromedriver (not chromedriver.exe), somewhere in your PATH '

downloads_path = os.path.join(home, 'Downloads')
script_path = os.path.split(os.path.realpath(__file__))[0]
log_path = os.path.join(script_path, 'log')
data_path = os.path.join(script_path, 'data')
for p in log_path, data_path:
    if not os.path.exists(p):
        os.mkdir(p)

private_settings_path = os.path.join(script_path, 'private_settings.py')
if not os.path.exists(private_settings_path):
    utils.log('ERROR: no private settings found, using defaults. Please edit %s' %
              private_settings_path)
    utils.log('Will not be able to access YNAB')
    private_settings_template_path = os.path.join(
        script_path, 'private_settings_template.py')
    shutil.copy(private_settings_template_path, private_settings_path)

budget_id = private_settings.budget_id
account_name = private_settings.account_name
api_key = private_settings.api_key

fail_on_ambiguous_transaction = False
' NOTE: you probalby want to make a category named as below '
default_category = 'ERROR'
close_browser_on_finish = False

' Always redownload csvs '
force_download_amazon = True

' TODO: variable controlling if transactions stay checked in the UI when done; currently they do '
' TODO: actually use log levels '
' TODO: classes instead of all these dictionaries '
' TODO: call get transactions via official ruby api '
' TODO: configurable amazon download length; currently 30 days '
