import argparse
import configparser
import json
import sys
from urllib.parse import urlparse

from lemmy import Lemmy


def get_config(cfile):
    config = configparser.ConfigParser(defaults={"exclude": ""}, interpolation=None)
    read = config.read(cfile)
    if not read:
        print(f"Could not read config {cfile}!")
        sys.exit(1)

    accounts = {i: dict(config.items(i)) for i in config.sections()}
    return accounts


def get_args():
    parser = argparse.ArgumentParser(
        prog="lemmy_migrate",
        description="Migrate subscribed communities from one account to another",
    )

    parser.add_argument(
        "-c", required=True, help="Path to config file", metavar="<config file>"
    )
    parser.add_argument(
        "-u",
        help="use to update main account subscriptions",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-e", help="Export main account subscriptions to json", metavar="<export file>"
    )
    parser.add_argument(
        "-i", help="Import subscriptions from json file", metavar="<import file>"
    )
    parser.add_argument(
        "-d", help="Dry run, make no modifications", action="store_true", default=False
    )
    args = parser.parse_args()
    return args


def sync_subscriptions(src_acct: Lemmy, dest_acct: Lemmy, from_backup, excld_comms):
    if from_backup:
        src_comms = from_backup
        print(f" {len(src_comms)} subscribed communities found from backup")
    else:
        print(" Getting list of subscribed communities from the two communities")
        print(
            f"\n[ Subscribing {dest_acct.site_url} to new communities from "
            f"{src_acct.site_url} ]"
        )

        src_comms = src_acct.get_communities()
        print(
            f" {len(src_comms)} subscribed communities found in the source"
            f" {src_acct.site_url}"
        )

    dest_comms = dest_acct.get_communities()
    print(
        f" {len(dest_comms)} subscribed communities found in the target"
        f" {dest_acct.site_url}"
    )

    # remove excludes
    exclds = None
    if excld_comms:
        exclds = excld_comms.split(",")

    new_communities = []
    for c in src_comms:
        if c not in dest_comms:
            # check exlucions
            if exclds is not None:
                if urlparse(c).path.split("/c/")[1] in exclds:
                    print(f"  {c} is excluded")
                else:
                    new_communities.append(c)
            else:
                new_communities.append(c)

    if new_communities:
        print(f" Subscribing to {len(new_communities)} new communities")
        dest_acct.subscribe(new_communities)


def write_backup(account: Lemmy, output: str) -> None:
    comms = account.get_communities()
    try:
        with open(output, "w") as f:
            json.dump({account.site_url: list(comms)}, f, indent=4)
    except Exception as e:
        print(f"  Error exporting file {output} -- {e}")
    else:
        print(f"  {len(comms)} Subscriptions backed up to {output}")


def read_backup(file: str) -> set | None:
    comms = None
    try:
        with open(file, "r") as f:
            data = json.load(f)
            comms = {c for k, v in data.items() for c in v}
    except Exception:
        print(f"   Failed to read import list {file}")

    return comms


def main():
    cfg = get_args()
    accounts = get_config(cfg.c)

    # set dry run
    Lemmy.dry_run = cfg.d

    if Lemmy.dry_run:
        print("\n*** DRY RUN enabled, no changes will be made ***")

    # source site
    print(f"\n[ Getting Main Account info -" f" {accounts['Main Account']['site']} ]")
    main_lemming = Lemmy(accounts["Main Account"]["site"])
    try:
        main_lemming.login(
            accounts["Main Account"]["user"], accounts["Main Account"]["password"]
        )
    except Exception as e:
        print(
            f"Unable to login to {accounts['Main Account']['site']}. Check your credentials and try again."
        )
        print(f"{e}")
        sys.exit(1)
    else:
        print(f" Logged into {accounts['Main Account']['site']}.")

    # export subscriptions
    if cfg.e:
        write_backup(main_lemming, cfg.e)
        return

    # import communites backed up if specified
    comms_backup = None
    if cfg.i:
        comms_backup = read_backup(cfg.i)
        # import to main account
        sync_subscriptions(None, main_lemming, comms_backup)

    accounts.pop("Main Account", None)

    # sync main account communities to each account
    for acc in accounts:
        print(f"\n[ Getting {acc} - {accounts[acc]['site']} ]")
        new_lemming = Lemmy(accounts[acc]["site"])
        try:
            new_lemming.login(accounts[acc]["user"], accounts[acc]["password"])
        except Exception as e:
            print(f"Unable to login to {acc}: {e}")
            print("Continuing to next account...")
            continue

        if cfg.u:
            print(" Update main flag set. Updating main account subscriptions")
            src = new_lemming
            dest = main_lemming
        else:
            src = main_lemming
            dest = new_lemming

        sync_subscriptions(src, dest, comms_backup, accounts[acc]["exclude"])


if __name__ == "__main__":
    main()
