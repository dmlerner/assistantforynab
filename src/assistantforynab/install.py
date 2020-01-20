from assistantforynab import settings
import os
import time
import shutil
import re

from webdriver_manager.chrome import ChromeDriverManager

from assistantforynab.utils import gui, utils


def restore_defaults():
    utils.log_info('Restoring default settings')
    for p in [settings.chromedriver_path, settings.settings_path]:
        if os.path.exists(p):
            utils.log_debug('removing', p)
            os.remove(p)

    for p in settings.log_dir, settings.data_dir, settings.backup_dir:
        if os.path.exists(p):
            utils.log_debug('removing', p)
            shutil.rmtree(p)

    settings.init()


def setup_chromedriver():
    if os.path.exists(settings.chromedriver_path):
        return
    utils.log_info('Installing Chromedriver')

    downloadPath = ChromeDriverManager(path = settings.chromedriver_dir).install()
    shutil.move(downloadPath, settings.chromedriver_path)
    shutil.rmtree(settings.chromedriver_dir + "/drivers")
    assert os.path.exists(settings.chromedriver_path)


def make_dirs():
    utils.log_info('Checking for directories')
    for p in settings.log_dir, settings.data_dir, settings.backup_dir:
        if not os.path.exists(p):
            utils.log_info('Making directory', p)
            os.mkdir(p)


def setup_ynab_auth():
    utils.log_info('Checking for YNAB authentication')
    # TODO: make this use oauth instead of api tokens
    if settings.get('api_token'):
        return
    utils.log_info('Installing YNAB authentication')
    api_token_url = 'https://app.youneedabudget.com/settings/developer'
    d = gui.driver()
    d.get(api_token_url)
    utils.log_info('Log in if needed')
    new_token_button = gui.get_by_text('button', 'New Token')
    gui.click(new_token_button)
    utils.log_info('Enter your password in the YNAB Web App, then click "Generate"')
    while 'New Personal Access Token' not in d.page_source:
        time.sleep(.5)
    api_token = re.search('New Personal Access Token: <strong>([^<]*)</strong>', d.page_source).groups()[0]
    settings.set('api_token', api_token)
    utils.log_debug('settings.api_token', settings.api_token)
    assert settings.api_token
    gui.quit()


def setup_ynab_budget_id():
    utils.log_info('Checking for selected budget')
    if settings.get('budget_id'):
        return
    utils.log_info('Selecting budget')
    url = 'https://app.youneedabudget.com/'
    driver = gui.driver()
    driver.get(url)
    utils.log_info('Log in if needed')
    while not re.search('youneedabudget.com/([^/]+)/', driver.current_url):
        time.sleep(.5)
    budget_selection_prompt = 'Press Enter when you have loaded the budget you want to use.'
    input(budget_selection_prompt)
    utils.log_debug(budget_selection_prompt)
    while not re.search('youneedabudget.com/([^/]+)/', driver.current_url):
        time.sleep(.5)
    settings.set('budget_id', re.search('youneedabudget.com/([^/]+)/', driver.current_url).groups()[0])
    utils.log_debug('settings.budget_id', settings.budget_id)
    assert settings.budget_id
    gui.quit()


def install():
    utils.log_info('Installing')
    setup_chromedriver()
    make_dirs()
    setup_ynab_auth()
    setup_ynab_budget_id()
    settings.init()
    utils.log_debug('Settings:', settings._s.settings)
    utils.log_info('Installed!')


if __name__ == '__main__':
    restore_defaults()
    install()
