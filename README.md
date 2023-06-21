# Migrate your subscribed Lemmy communities from one account to another

## Usage
```
usage: lemmy_migrate [-h] -c config_file

Migrate subscribed communities from one account to another

options:
  -h, --help      show this help message and exit
  -c config_file  Path to config file
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