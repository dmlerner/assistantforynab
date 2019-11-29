import traceback
import sys
import time
import subprocess
import signal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.command import Command

import ynabassistant as ya


def get(class_name, count=None, require=True, predicate=None, wait=30, pause=.25):
    ya.utils.log_debug('get', class_name)
    start = time.time()
    predicate = predicate or bool  # bool serves as the identity
    matches = None
    while not matches and time.time() - start < wait:
        class_elements = driver().find_elements_by_class_name(class_name)
        matches = list(filter(predicate, class_elements))
        time.sleep(pause)
    if require:
        assert matches
        if count is not None:
            assert len(matches) == count
    if len(matches) == 1:
        return matches[0]
    return matches


def scroll_to(element):
    driver().execute_script('arguments[0].scrollIntoView(true);', element)


def get_width():
    return window_size()['width']


def get_height():
    ya.utils.log_info('height', window_size()['height'])
    return window_size()['height']


def window_size():
    return driver().get_window_size(windowHandle='current')


def get_by_placeholder(class_name, p, count=None, require=True, wait=30):
    ya.utils.log_debug('get_by_placeholder', class_name, p)
    if isinstance(p, str):
        p = (p,)
    return get(class_name, count, require, lambda e: e.get_attribute('placeholder') in p, wait)


def get_by_text(class_name, t, count=None, require=True, wait=30, partial=False):
    ya.utils.log_debug('get_by_text', class_name, t)
    if isinstance(t, str):
        t = (t,)
    if partial:
        return get(class_name, count, require, lambda e: any(T in e.text for T in t), wait)
    return get(class_name, count, require, lambda e: e.text in t, wait)


def click(element, n=1, pause=.5):
    ya.utils.log_debug('click')
    if type(element) in (tuple, list):
        element = element[0]
    for i in range(n):
        driver().execute_script('arguments[0].click();', element)
        if i != n - 1:
            time.sleep(pause)


def right_click(element):
    ya.utils.log_debug('right_click')
    if type(element) in (tuple, list):
        element = element[0]
    actions = ActionChains(driver())
    actions.context_click(element).perform()


def send_keys(keys):
    ya.utils.log_debug('send_keys', keys)
    actions = ActionChains(driver())
    actions.send_keys(keys).perform()


def close_orphan_drivers():
    return
    # TODO: this doesn't work from WSL
    ya.utils.log_debug('close_orphan_drivers')
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        if 'chromedriver.exe' in str(line.lower()):
            pid = int(line.split(None, 1)[0])
            ya.utils.log_debug('killing', line, pid)
            os.kill(pid, signal.SIGKILL)


_driver = None


def driver():
    ya.utils.log_debug('driver')
    global _driver
    try:
        if is_alive(_driver):
            return _driver
        close_orphan_drivers()
        options = Options()
        options.add_argument('user-data-dir={}'.format(ya.settings.chrome_data_dir))
        options.add_argument('--disable-extensions')
        _driver = webdriver.Chrome(options=options)
    except BaseException:
        quit()
        if 'data directory is already in use' in traceback.format_exc():
            ya.utils.log_exception_debug()
            ya.utils.log_error('Must close Selenium-controlled Chrome.')
            if input('Try again? [Y/n]\n').lower() != 'n':
                ya.utils.log_info('Trying again')
                return driver()
            sys.exit()
        else:
            ya.utils.log_exception()
    return _driver


def quit():
    if is_alive(_driver):
        _driver.quit()


def is_alive(d):
    ya.utils.log_debug('is_alive')
    try:
        d.execute(Command.STATUS)
        return True
    except BaseException:
        ya.utils.log_exception_debug()
        return False


def zoom(z):
    driver().execute_script("document.body.style.zoom='" + str(int(z)) + "%'")
