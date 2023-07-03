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
    parser.add_argument('-u', '--update-main',
                        help="use to update main account subscriptions",
                        default=False,
                        action='store_true')

    args = parser.parse_args()
    return args


def sync_subscriptions(src_acct, dest_acct):
    print(f"\n[ Subscribing {dest_acct._site_url} to new communities from {src_acct._site_url} ]")
    print('getting list of subscribed communities from the two communities')
    src_comms = src_acct.get_communities()
    print(f" {len(src_comms)} subscribed communities found in the source")
    dest_comms = dest_acct.get_communities()
    print(f" {len(dest_comms)} subscribed communities found in the target")

    new_communities = {c: src_comms[c] for c in src_comms if c not in dest_comms}

    if new_communities:
        print(f" Subscribing to {len(new_communities)} new communities")
        dest_acct.subscribe(new_communities)

def main():
    cfg = get_args()
    accounts = get_config(cfg.c)
    update_main = cfg.update_main

    # source site
    print(f"\n[ Getting Main Account info - {accounts['Main Account']['site']} ]")
    main_lemming = Lemmy(accounts['Main Account']['site'])
    main_lemming.login(accounts['Main Account']['user'],
                accounts['Main Account']['password'])
    accounts.pop('Main Account', None)

    # sync main account communities to each account
    for acc in accounts:
        print(f"\n[ Getting {acc} - {accounts[acc]['site']} ]")
        new_lemming = Lemmy(accounts[acc]['site'])
        new_lemming.login(accounts[acc]['user'], accounts[acc]['password'])

        if update_main:
            print('update_main flag set. updating main account subscriptions')
            src = new_lemming
            dest = main_lemming
        else:
            src = main_lemming
            dest = new_lemming

        sync_subscriptions(src, dest)


if __name__ == "__main__":
    main()
