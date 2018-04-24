import argparse
from jackal.utils import print_line, print_json
from jackal import UserSearch


def main():
    user_search = UserSearch()
    arg = argparse.ArgumentParser(
        parents=[user_search.argparser], conflict_handler='resolve')
    arg.add_argument(
        '-c', '--count', help="Only show the number of results", action="store_true")
    arguments = arg.parse_args()

    if arguments.count:
        print_line("Number of hosts: {}".format(user_search.argument_count()))
    else:
        response = user_search.get_users()
        for hit in response:
            print_json(hit.to_dict(include_meta=True))
