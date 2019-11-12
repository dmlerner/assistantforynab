This is an alpha version. Use at your own risk.

I suggest backing up your budget before using this!

Tested on windows linux subsystem, ubuntu 18.04, windows 10, cmder/zsh

See various notes in settings.py

Currently depends on [an unofficial python api](https://github.com/andreroggeri/ynab-sdk-python) with two files modified slightly
	I've included the two files in my repo. You'll have to manually copy them over:
	cp default_client.py ~/.local/lib/python3.8/site-packages/ynab_sdk/utils/clients/
	cp transactions.py ~/.local/lib/python3.8/site-packages/ynab_sdk/api/

I'm sure you'll have to pip install some things. I'll hopefuly add instructions soon.

The thing that is most fragile is definitely entering in the gui itself. That would not even be necessary, except that the API [doesn't support split transactions.](https://support.youneedabudget.com/t/m251v5/posting-split-transactions) 
