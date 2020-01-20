from setuptools import find_packages, setup

setup(
    name="assistantforynab",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=['ynab_api', 'jsonpickle', 'selenium', 'webdriver-manager', 'requests'],
    package_data={
        '': ['default_settings.json'],
    }
)
