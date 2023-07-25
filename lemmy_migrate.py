import sys
import argparse
import configparser
import json
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
    parser.add_argument('-e', help="Export main account subscriptions to json",
                        metavar="export")
    parser.add_argument('-i', help="Import subscriptions from json file",
                        metavar='import')
    args = parser.parse_args()
    return args


def sync_subscriptions(src_acct: Lemmy, dest_acct: Lemmy, fimport):
    print(f"\n[ Subscribing {dest_acct.site_url} to new communities from "
          f"{src_acct.site_url} ]")
    print(' Getting list of subscribed communities from the two communities')
    src_comms = src_acct.get_communities()
    print(f" {len(src_comms)} subscribed communities found in the source"
          f" {src_acct.site_url}")
    if fimport:
        dest_comms = fimport
    else:
        dest_comms = dest_acct.get_communities()

    print(f" {len(dest_comms)} subscribed communities found in the target"
          f" {dest_acct.site_url}")

    new_communities = [c for c in src_comms if c not in dest_comms]

    if new_communities:
        print(f" Subscribing to {len(new_communities)} new communities")
        dest_acct.subscribe(new_communities)


def export(account: Lemmy, output: str):
    comms = account.get_communities()
    try:
        with open(output, "w") as f:
            json.dump({account.site_url: comms}, f, indent=4)
    except Exception as e:
        print(f"  Error exporting file {output} -- {e}")
    else:
        print(f"  Subscriptions backed up to {output}")


def read_import(file: str) -> list | None:
    comms = None
    try:
        with open(file, "r") as f:
            data = json.load(f)
            comms = [c for k, v in data.items() for c in v]
    except Exception:
        print(f"   Failed to read import list {file}")

    return comms


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

    # export subscriptions
    if cfg.e:
        export(main_lemming, cfg.e)
        return

    # import communites backed up if specified
    comms_backup = None
    if cfg.i:
        comms_backup = read_import(cfg.i)
    
    # sync main account communities to each account
    for acc in accounts:
        print(f"\n[ Getting {acc} - {accounts[acc]['site']} ]")
        new_lemming = Lemmy(accounts[acc]['site'])
        new_lemming.login(accounts[acc]['user'], accounts[acc]['password'])

        if update_main:
            print(' Update main flag set. Updating main account subscriptions')
            src = new_lemming
            dest = main_lemming
        else:
            src = main_lemming
            dest = new_lemming

        sync_subscriptions(src, dest, comms_backup)


if __name__ == "__main__":
    main()
