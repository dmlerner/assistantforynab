# contains non user facing settings
import os
import datetime
import platform

start_time = datetime.datetime.now()

home = os.path.expanduser('~')

downloads_dir = os.path.join(home, 'Downloads')

settings_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(settings_dir)


def guess_os():
    if platform.system() == 'Linux':
        if 'Microsoft' not in platform.release():
            os = 'linux'
        os = 'windows'
    elif platform.system() == 'Windows':
        os = 'windows'
    else:
        os = 'mac'
    return os


operating_system = guess_os()


chromedriver_dir = os.path.join(root_dir, 'utils')
chromedriver_filenames = {
    'windows': 'chromedriver.exe',
    'mac': 'chromedriver',
    'linux': 'chromedriver',
}
chromedriver_path = os.path.join(chromedriver_dir, chromedriver_filenames[operating_system])


chrome_data_dirs = {
    'windows': 'AppData/Local/Google/Chrome/User Data/Default',
    'mac': 'Library/Application Support/Google/Chrome/Default',
    'linux': '.config/google-chrome/default',
}
chrome_data_dir = os.path.join(home, chrome_data_dirs[operating_system])

log_dir = os.path.join(root_dir, 'log')
data_dir = os.path.join(root_dir, 'data')
backup_dir = os.path.join(root_dir, 'backups')

for d in log_dir, data_dir, backup_dir:
    if not os.path.exists(d):
        os.mkdir(d)

settings_path = os.path.join(settings_dir, 'settings.json')
default_settings_path = os.path.join(settings_dir, 'default_settings.json')
