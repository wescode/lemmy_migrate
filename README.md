# Migrate your subscribed Lemmy communities from one account to another

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
```
[Main Account] is required for your primary account, and you can have as many secondary accounts as you wish. Label for
secondary accounts can be anything.