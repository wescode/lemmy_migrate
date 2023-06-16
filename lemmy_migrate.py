import argparse
from lemmy import Lemmy

parser = argparse.ArgumentParser(
                    prog='lemmy_migrate',
                    description='Migrate subscribed communities from one account to another')
parser.add_argument('-s', required=True, help='Source site URL', metavar='source_site')
parser.add_argument('-a', required=True, help='Source account', metavar='source_account')
parser.add_argument('-p', required=True, help='Source password', metavar='source_password')
parser.add_argument('-d', help='Destination site URL', required=True, metavar='destination_site')
parser.add_argument('-l', help='Destination account', required=True, metavar='destination_account')
parser.add_argument('-c', help='Destination password', required=True, metavar='destination_password')
args = parser.parse_args()

# source site
lemming = Lemmy(args.s)
lemming.login(args.a, args.p)
communties = lemming.get_communities()

# destination site
new_lemming = Lemmy(args.d)
new_lemming.login(args.l, args.c)
new_lemming.get_communities()
new_lemming.subscribe(communties)
