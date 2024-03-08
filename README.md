# Lemmy Migrate
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
## Migrate your subscribed Lemmy communities from one account to another

## Usage
```
usage: lemmy_migrate [-h] -c <config file> [-u] [-e <export file>] [-i <import file>]

Migrate subscribed communities from one account to another

options:
  -h, --help        show this help message and exit
  -c <config file>  Path to config file
  -u                use to update main account subscriptions
  -e <export file>  Export main account subscriptions to json
  -i <import file>  Import subscriptions from json file
  -d                DryRun, make no changes

```
## Run
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python lemmy_migrate.py
```

## Configuration
Operation is now controlled by a configuration file as such:

```
[Main Account]
Site = https://sh.itjust.works
User = Imauser
Password = apasswod

[Account 2]
Site = https://lemmy.ml
User = cooluser
Password = badpassword
Exclude = news,politics
```
[Main Account] is required for your primary account, and you can have as many secondary accounts as you wish. Label for
secondary accounts can be anything.


## Requirements
Python >= 3.10
requests