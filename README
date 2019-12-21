
**This is an alpha version. Use at your own risk. I suggest backing up your budget first.**
# What's this?
[YNAB](ynab.com) is excellent budgeting software, but is missing some essential features:

1) Backup and restore your budget
2) Split Amazon transactions into individual, labeled items
3) API for adding/modifying split transactions
4) Automatic distribution of funds to meet category goals
5) Goals on a specific date


![Demo GIF](demo.gif)

See various notes and settings in settings.py

# Installation:

```
pip3 install ynabassistant
mkdir $YOUR_CHOICE_OF_DIRECTORY_NAME  
cd $YOUR_CHOICE_OF_DIRECTORY_NAME
git clone http://www.github.com/dmlerner/ynabassistant.git
virtualenv -p $(which python3) .
source ./bin/activate
pip3 install selenium jsonpickle ynab_api
deactivate
cd ynabamazonparser
```


# Use:

```
source $YOUR_CHOICE_OF_DIRECTORY_NAME/bin/activate
python3 -m ynabamazonparser $YOUR_CHOICE_OF_DIRECTORY_NAME/ynabamazonparser/driver.py
deactivate
```


Which you may want to alias, eg by adding to your ~/.zshrc or similar:

```
function ya() {
	root=$YOUR_CHOICE_OF_DIRECTORY_NAME
	source $root/bin/activate
	python3 $root/ynabamazonparser/driver.py
	deactivate
}
```

So then you can just run from anywhere as:

```
ya
```
