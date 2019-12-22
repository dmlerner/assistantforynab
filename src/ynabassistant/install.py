import settings
import os
import time
import shutil
import zipfile
import requests
import re


from utils import gui


def clean():
    print('clean')
    for p in [settings.chromedriver_path, settings.settings_path]:
        if os.path.exists(p):
            print('removing', p)
            os.remove(p)

    for p in settings.log_dir, settings.data_dir, settings.backup_dir:
        if os.path.exists(p):
            print('removing', p)
            shutil.rmtree(p)


clean()


# TODO: log, not print


def setup_chromedriver():
    print('setup_chromedriver')
    if os.path.exists(settings.chromedriver_path):
        return
    chromedriver_url = 'https://chromedriver.storage.googleapis.com/79.0.3945.36/chromedriver_win32.zip'
    chromedriver_zip_filename = os.path.basename(chromedriver_url)
    response = requests.get(chromedriver_url)
    with open(chromedriver_zip_filename, 'wb') as f:
        f.write(response.content)
    with zipfile.ZipFile(chromedriver_zip_filename, 'r') as f:
        f.extractall(settings.chromedriver_dir)
    os.remove(chromedriver_zip_filename)
    assert os.path.exists(settings.chromedriver_path)


def setup_ynab_auth():
    print('setup_ynab_auth')
    # TODO: make this use oauth instead of api tokens
    if settings.get('api_token'):
        return
    api_key_url = 'https://app.youneedabudget.com/settings/developer'
    gui.driver().get(api_key_url)
    print('Log in, then click "New Token"')
    api_token = input('Enter token value:\n')  # TODO: scrape
    settings.set('api_token', api_token)
    print('api_token=', settings.api_token)
    assert settings.api_token


def setup_ynab_budget_id():
    print('setup_ynab_budget_id')
    if settings.get('budget_id'):
        return
    url = 'https://app.youneedabudget.com/'
    driver = gui.driver()
    driver.get(url)
    print('Log in')
    while not re.search('youneedabudget.com/([^/]+)/', driver.current_url):
        time.sleep(.5)
    input('Press Enter when you have loaded the budget you want to use.')
    while not re.search('youneedabudget.com/([^/]+)/', driver.current_url):
        time.sleep(.5)
    settings.set('budget_id', re.search('youneedabudget.com/([^/]+)/', driver.current_url).groups()[0])
    #settings.set('budget_id', 'poopbudget')
    print('settings.budget_id=', settings.budget_id)
    assert settings.budget_id


def make_dirs():
    print('make_dirs')
    for p in settings.log_dir, settings.data_dir, settings.backup_dir:
        if not os.path.exists(p):
            os.mkdir(p)


clean()
print('clean')
setup_chromedriver()
print('setup_chromedriver')
make_dirs()
print('make_dirs')
setup_ynab_auth()
print('setup_ynab_auth')
setup_ynab_budget_id()
print('setup_ynab_budget_id')
print(vars(settings).keys())
gui.driver().close()
