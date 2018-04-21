import argparse
import webbrowser
import getpass


def signup(args):
    webbrowser.open('https://jar.place/')


def login(args):
    user = input("Username [%s]: " % getpass.getuser())
    if not user:
        user = getpass.getuser()

    pprompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))

    p1, p2 = pprompt()
    while p1 != p2:
        print('Passwords do not match. Try again')
        p1, p2 = pprompt()

    return user, p1


def main():
    args.func(args)


parser = argparse.ArgumentParser(description='CLI for JarPlace (https://jar.place/)')

subparsers = parser.add_subparsers(help='sub-command help')

parser_signup = subparsers.add_parser('signup')
parser_signup.set_defaults(func=signup)

parser_login = subparsers.add_parser('login')
parser_login.set_defaults(func=login)

args = parser.parse_args()
