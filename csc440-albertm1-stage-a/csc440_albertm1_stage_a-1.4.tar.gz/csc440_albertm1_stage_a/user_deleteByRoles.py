"""Tool for deleting user entries by role from within a json file in a given directory.

This module 'user_deletebyRoles.py' can be used to delete all users from the wiki440 database if they have the role
specified during command line execution.

Command line usage:
user_deleteByRoles.py [-h] [--file FILE] [--role ROLE]

Options:

positional arguments:
  file            The full directory file-path to the JSON file of wiki users you want to delete from.
  role            The specific role that a user should have in their data to qualify them for deletion.

optional arguments:
  -h, --help      Show the help message and exit.
"""

import os
import argparse
import pydoc
from csc440_albertm1_stage_a.user_createdelete import read_file
from csc440_albertm1_stage_a.user_createdelete import delete_users_by_role


def main():
    parser = argparse.ArgumentParser(description='This script can delete all users from the wiki database that have a specific role associated to them.')
    parser.add_argument('-f', '--file', help='Full path to the JSON file from which you want to delete some users. Write access required for file.', required=True)
    parser.add_argument('-r', '--role', help='The role of the users that should qualify user for deletion.', required=True)
    args = vars(parser.parse_args())
    if os.path.exists(args['file']):
        print("Found OS path\n")
        current_users_list = read_file(args['file'])
        print("\nList of current users:\n", current_users_list)
        revised_users_list = delete_users_by_role(args['file'], args['role'])
        if not revised_users_list:
            print("ERROR: JSON file could not be revised!")
        else:
            print("\nRevised users list:\n", revised_users_list)


if __name__ == '__main__':
    main()
