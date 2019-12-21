import os
import config
import shutil
import zipfile
import requests
import settings
import re
import ynabassistant.utils.gui
# TODO: log, not print


def clean():
    for p in [config.chromedriver_path, config.settings_path]:
        if os.path.exists(p):
            os.remove(p)

    for p in config.log_dir, config.data_dir, config.backup_dir:
        if os.path.exists(p):
            os.removedirs(p)


def copy_default_settings():
    if os.path.exists(config.settings_path):
        return
    shutil.copy(config.default_settings_path, config.settings_path)


def setup_chromedriver():
    if os.path.exists(config.chromedriver_path):
        return
    chromedriver_url = 'https://chromedriver.storage.googleapis.com/79.0.3945.36/chromedriver_win32.zip'
    chromedriver_zip_filename = os.path.basename(chromedriver_url)
    response = requests.get(chromedriver_url)
    with open(chromedriver_zip_filename, 'wb') as f:
        f.write(response.content)
    with zipfile.ZipFile(chromedriver_zip_filename, 'r') as f:
        f.extractall(config.chromedriver_dir)
    os.remove(chromedriver_zip_filename)
    assert os.path.exists(config.chromedriver_path)


def setup_ynab_auth():
    # TODO: make this use oauth instead of api tokens
    if settings.api_token:
        return
    api_key_url = 'https://app.youneedabudget.com/settings/developer'
    ynabassistant.utils.gui.driver().get(api_key_url)
    print('Log in, then click "New Token"')
    api_token = input('Enter token value:\n')  # TODO: scrape
    settings.api_token = api_token
    settings.save()
    assert settings.api_token


def setup_ynab_budget_id():
    if settings.budget_id:
        return
    url = 'https://app.youneedabudget.com/'
    driver = ynabassistant.utils.gui.driver()
    driver.get(url)
    print('Log in')
    settings.bugdet_id = re.search('youneedabudget.com/([^/]+)/', driver.current_url)
    print(settings.budget_id)
    settings.save()


def make_dirs():
    for p in config.log_dir, config.data_dir, config.backup_dir:
        if not os.path.exists(p):
            os.mkdir(p)


clean()
make_dirs()
setup_chromedriver()
setup_ynab_auth()
setup_ynab_budget_id()
print(vars(settings))
