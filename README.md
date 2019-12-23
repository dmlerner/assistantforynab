**This is an alpha version. Use at your own risk. I suggest backing up your budget first.**
# What's this?
[YNAB](ynab.com) is excellent budgeting software, but is missing some essential features:

1) Backup and restore your budget
2) Split Amazon transactions into individual, labeled items
3) API for adding/modifying split transactions
4) Delete transactions

Work in progress:

5) Automatic distribution of funds to meet category goals
6) Goals on a specific date


# Installation:
Clone the repo:
```
mkdir $YOUR_CHOICE_OF_DIRECTORY_NAME  
cd $YOUR_CHOICE_OF_DIRECTORY_NAME
git clone http://github.com/dmlerner/assistantforynab.git
cd assistantforynab
```

Optionally, make a virtual environment:
```
python3 -m venv env
source ./env/bin/activate
```
Install:
```
python3 setup.py install
```

# Use:

```
source $YOUR_CHOICE_OF_DIRECTORY_NAME/env/bin/activate
python3
```
```
>>> from assistantforynab import Assistant
>>> Assistant.full_handle_amazon()
```
`deactivate`

For more ideas of what it can do, check out [assistantforynab.assistant.py](https://github.com/dmlerner/assistantforynab/blob/dev/src/assistantforynab/assistant/assistant.py)

# FAQ:

 1. Does this jeopardize my credentials or YNAB data?
	 No. It uses the official YNAB API and goes through the same servers as if you use the webapp. I generated [Python binding](https://github.com/dmlerner/ynab-apis) from the official swagger spec using OpenAPI Generator, and made zero modifications. 
2. Does this store my data?
     Yes, but only on whatever computer you use to run it. This is for backup purposes, and easy to disable.
3. Why does this ask for my API Token? 
     Because it's an alpha version and I haven't gotten around to making it work with OAuth. The token is sent to YNAB, but not to anywhere else.
