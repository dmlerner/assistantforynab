# contains non user facing settings
import os

home = os.path.expanduser('~')

downloads_dir = os.path.join(home, 'Downloads')

config_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(config_dir)

chromedriver_dir = os.path.join(root_dir, 'utils')
chromedriver_path = os.path.join(chromedriver_dir, 'chromedriver.exe')

# This is likely only correct for Windows
chrome_data_dir = os.path.join(home, '/AppData/Local/Google/Chrome/User Data/Default')

log_dir = os.path.join(root_dir, 'log')
data_dir = os.path.join(root_dir, 'data')
backup_dir = os.path.join(root_dir, 'backups')
settings_path = os.path.join(config_dir, 'settings.json')
default_settings_path = os.path.join(config_dir, 'default_settings.json')
