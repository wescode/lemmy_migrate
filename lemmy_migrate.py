import sys
import argparse
import configparser
from lemmy import Lemmy


def get_config(cfile):
    config = configparser.ConfigParser(interpolation=None)
    read = config.read(cfile)
    if not read:
        print(f"Could not read config {cfile}!")
        sys.exit(1)

    accounts = {i: dict(config.items(i)) for i in config.sections()}
    return accounts

def get_args():
    parser = argparse.ArgumentParser(
        prog='lemmy_migrate',
        description='Migrate subscribed communities from one account to another')

    parser.add_argument('-c', required=True, help="Path to config file",
                        metavar="config_file") 
    args = parser.parse_args()
    return args.c

def main():
    cfg = get_args()
    accounts = get_config(cfg)

    # source site
    print(f"\n[ Getting Main Account info - {accounts['Main Account']['site']} ]")
    lemming = Lemmy(accounts['Main Account']['site'])
    lemming.login(accounts['Main Account']['user'], 
                accounts['Main Account']['password'])
    communties = lemming.get_communities()
    print(f" {len(communties)} subscribed communities found")
    accounts.pop('Main Account', None)

    # sync main account communities to each account
    for acc in accounts:
        print(f"\n[ Syncing {acc} - {accounts[acc]['site']} ]")
        new_lemming = Lemmy(accounts[acc]['site'])
        new_lemming.login(accounts[acc]['user'], accounts[acc]['password'])
        comms = new_lemming.get_communities()
        print(f" {len(comms)} subscribed communities found")
        new_communities = {c: communties[c] for c in communties if c not in comms}
        
        if new_communities:
            print(f" Subscribing to {len(new_communities)} new communities")
            new_lemming.subscribe(new_communities)

if __name__ == "__main__":
    main()
