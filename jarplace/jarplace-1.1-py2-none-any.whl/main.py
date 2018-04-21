import argparse
from main import auth
from main import billing
from main import repo
from main import user


def main():
    args.func(args)


# Top parsers
top_parser = argparse.ArgumentParser(description='CLI for JarPlace (https://jar.place/)')
top_subparsers = top_parser.add_subparsers(dest='command', help='Available commands')
top_subparsers.required = True

# Signup parsers
top_subparser_signup = top_subparsers.add_parser('signup', help='Sign up for the service')
top_subparser_signup.set_defaults(func=auth.signup)

# Login
top_subparser_login = top_subparsers.add_parser('login', help='Authentication and authorization')
top_subparser_login.set_defaults(func=auth.login)

# Billing parsers
top_subparser_billing = top_subparsers.add_parser('billing', help='Billing management')

billing_subparsers = top_subparser_billing.add_subparsers(dest='command', help='Billing management')
billing_subparsers.required = True

billing_subparser_plan = billing_subparsers.add_parser('list', help='List all plans')
billing_subparser_plan.set_defaults(func=billing.show)

billing_subparser_plan = billing_subparsers.add_parser('plan', help='Show current plan')
billing_subparser_plan.set_defaults(func=billing.plan)

billing_subparser_change = billing_subparsers.add_parser('change', help='Change plan')
billing_subparser_change.set_defaults(func=billing.change)
billing_subparser_change.add_argument('name')

# Repo parsers
top_subparser_repo = top_subparsers.add_parser('repo', help='Repositories management')

repo_subparsers = top_subparser_repo.add_subparsers(dest='command', help='Repositories management')
repo_subparsers.required = True

repo_subparser_list = repo_subparsers.add_parser('list', help='List all repositories')
repo_subparser_list.set_defaults(func=repo.show)

repo_subparser_info = repo_subparsers.add_parser('info', help='Show repository details')
repo_subparser_info.set_defaults(func=repo.info)
repo_subparser_info.add_argument('name')

repo_subparser_create = repo_subparsers.add_parser('create', help='Create new repository')
repo_subparser_create.set_defaults(func=repo.create)
repo_subparser_create.add_argument('name')
repo_subparser_create.add_argument('--private', dest='private', action='store_const', const='true', default='false')

repo_subparser_modify = repo_subparsers.add_parser('modify', help='Modify existing repository')
repo_subparser_modify.set_defaults(func=repo.modify)
repo_subparser_modify.add_argument('name')
repo_subparser_modify.add_argument('--private', dest='private', action='store_const', const='true', default='false')

repo_subparser_delete = repo_subparsers.add_parser('delete', help='Delete repository')
repo_subparser_delete.set_defaults(func=repo.delete)
repo_subparser_delete.add_argument('name')

# User parsers
top_subparser_user = top_subparsers.add_parser('user', help='User management')

user_subparsers = top_subparser_user.add_subparsers(dest='command', help='User management')
user_subparsers.required = True

user_subparser_list = user_subparsers.add_parser('list', help='List all users')
user_subparser_list.set_defaults(func=user.show)
user_subparser_list.add_argument('--repo', required=True, dest='repo')

user_subparser_info = user_subparsers.add_parser('info', help='Show user details')
user_subparser_info.set_defaults(func=user.info)
user_subparser_info.add_argument('name')
user_subparser_info.add_argument('--repo', required=True, dest='repo')

user_subparser_create = user_subparsers.add_parser('create', help='Create new user')
user_subparser_create.set_defaults(func=user.create)
user_subparser_create.add_argument('name')
user_subparser_create.add_argument('--repo', required=True, dest='repo')
user_subparser_create.add_argument('--password', required=True, dest='password')
user_subparser_create.add_argument('--readonly', dest='readonly', action='store_const', const='true', default='false')

user_subparser_modify = user_subparsers.add_parser('modify', help='Modify existing user')
user_subparser_modify.set_defaults(func=user.modify)
user_subparser_modify.add_argument('name')
user_subparser_modify.add_argument('--repo', required=True, dest='repo')
user_subparser_modify.add_argument('--password', required=False, dest='password')
user_subparser_modify.add_argument('--readonly', dest='readonly', action='store_const', const='true', default='false')

user_subparser_delete = user_subparsers.add_parser('delete', help='Delete user')
user_subparser_delete.set_defaults(func=user.delete)
user_subparser_delete.add_argument('name')
user_subparser_delete.add_argument('--repo', required=True, dest='repo')

args = top_parser.parse_args()
