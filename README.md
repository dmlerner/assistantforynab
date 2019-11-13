This is an alpha version. Use at your own risk.

I suggest backing up your budget before using this!

Tested on windows linux subsystem, ubuntu 18.04, windows 10, cmder/zsh

See various notes in settings.py

Currently depends on [an unofficial python api](https://github.com/andreroggeri/ynab-sdk-python) with two files modified slightly
	I've included the two files in my repo. You'll have to manually copy them over:
	cp default_client.py ~/.local/lib/python3.8/site-packages/ynab_sdk/utils/clients/
	cp transactions.py ~/.local/lib/python3.8/site-packages/ynab_sdk/api/
Hopefully I'll remove this dependency soon.

The thing that is most fragile is definitely entering in the gui itself. That would not even be necessary, except that the API [doesn't support split transactions.](https://support.youneedabudget.com/t/m251v5/posting-split-transactions) 

.............................

Installation:

`
mkdir $YOUR_CHOICE_OF_DIRECTORY_NAME 

cd $YOUR_CHOICE_OF_DIRECTORY_NAME

git clone http://www.github.com/dmlerner/ynabamazonparser.git

virtualenv -p $(which python3) .

source ./bin/activate

pip3 install selenium ynab_sdk

cd ynabamazonparser

cp transactions.py ../lib/python3.8/site-packages/ynab_sdk/api

cp default_client.py ../lib/python3.8/site-packages/ynab_sdk/utils/clients

python3 driver.py

deactivate
`

......................


Running in general:

`
source $YOUR_CHOICE_OF_DIRECTORY_NAME/bin/activate

python3 $YOUR_CHOICE_OF_DIRECTORY_NAME/ynabamazonparser/driver.py
`

................................


Which you may want to alias, eg by adding to your ~/.zshrc or similar:

`
function yap() {

	root = $YOUR_CHOICE_OF_DIRECTORY_NAME

	source $root/bin/activate

	python3 $root/ynabamazonparser/driver.py

	deactivate

}
`

So then you can just run from anywhere as:

`
yap
`	
