from distutils.core import setup
setup(
  name='ynabamazonparser',
  packages=['ynabamazonparser'],
  version='0.1.1',
  license='MIT',
  description='Downloads Amazon purchase history and enters it into YNAB',
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
    'Programming Language :: Python :: 3.8',
  ],
)
