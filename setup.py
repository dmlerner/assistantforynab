from setuptools import find_packages, setup

setup(
    name="ynabassistant",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=['ynab_api', 'jsonpickle', 'selenium'],
)
