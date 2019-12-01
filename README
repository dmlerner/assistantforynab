
**This is an alpha version. Use at your own risk. I suggest backing up your budget first.**
# What's this?
[YNAB](ynab.com) is excellent budgeting software, but is missing some essential features:

1) Automatic distribution of funds to meet category goals
2) Goals on a specific date
3) Backup and restore your budget
4) Split Amazon transactions into individual, labeled items
5) API for adding/modifying split transactions


![Demo GIF](demo.gif)

See various notes and settings in settings.py

# Installation:

```
mkdir $YOUR_CHOICE_OF_DIRECTORY_NAME  
cd $YOUR_CHOICE_OF_DIRECTORY_NAME
git clone http://www.github.com/dmlerner/ynabamazonparser.git
virtualenv -p $(which python3) .
source ./bin/activate
pip3 install selenium ynab_sdk
deactivate
cd ynabamazonparser
cp transactions.py ../lib/python3.8/site-packages/ynab_sdk/api
cp default_client.py ../lib/python3.8/site-packages/ynab_sdk/utils/clients
```


# Use:

```
source $YOUR_CHOICE_OF_DIRECTORY_NAME/bin/activate
python3 -m ynabamazonparser $YOUR_CHOICE_OF_DIRECTORY_NAME/ynabamazonparser/driver.py
deactivate
```


Which you may want to alias, eg by adding to your ~/.zshrc or similar:

```
function yap() {
	root=$YOUR_CHOICE_OF_DIRECTORY_NAME
	source $root/bin/activate
	python3 $root/ynabamazonparser/driver.py
	deactivate
}
```

So then you can just run from anywhere as:

```
yap
```
