from distutils.core import setup
setup(
  name='ynabassistant',
  packages=['ynabassistant'],
  version='0.1.2',
  license='MIT',
  description='Automatically move funds to reach goals, and imports detailed Amazon data',
  author='David Lerner',
  author_email='dmlerner@gmail.com',
  url='https://github.com/dmlerner/ynabamazonparser',
  download_url='https://github.com/dmlerner/ynabamazonparser/archive/v0.1.1.tar.gz',
  keywords=['YNAB', 'Amazon', 'Budget'],
  install_requires=[
      'selenium',
      'ynab_sdk',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
  ],
)
