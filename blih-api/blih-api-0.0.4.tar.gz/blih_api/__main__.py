# -*- coding: utf-8 -*-

import sys
import argparse
from blih_api.repository.api import RepositoryApi
from blih_api.sshkey.api import SSHKeyApi


class BlihCLI:

    @classmethod
    def cli(cls, argv=[]):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(help='What you want to manage ?', dest="command")

        # Main Parser
        parser.add_argument('--verbose', action='store_true', help='Verbose')
        parser.add_argument('--username', type=str, help='Your Epitech username (email e.q prenom.nom@epitech.eu)')
        parser.add_argument('--password',
                            type=str,
                            help='Your Epitech hashed password (sha512) '
                                 '(sh -c "echo -ne PASSWORD | sha512sum | tr -d \'\\n-\'")')

        # SSHKey Parser
        sshkey_parser = subparsers.add_parser('sshkeys', help="Manage your SSH keys")
        sshkey_subparsers = sshkey_parser.add_subparsers(help="what do you want to do with your SSH keys ?",
                                                         dest="sshkey_action")
        sshkey_subparsers.add_parser('list', help="List your SSH keys")

        s_add_sub = sshkey_subparsers.add_parser('add', help="Add an SSH key to your list")
        s_add_sub.add_argument('--value', type=str, required=True, help="SSH key value (e.g `cat ~/.ssh/ida_rsa.pub`)")

        s_add_sub = sshkey_subparsers.add_parser('remove', help="Remove an SSH key to your list")
        s_add_sub.add_argument('--name', type=str, required=True, help="SSH key name (see SSH key listing)")

        # Repository Parser
        repository_parser = subparsers.add_parser('repositories', help="Manage your repositories")
        repository_subparsers = repository_parser.add_subparsers(help="what do you want to do with your repositories ?",
                                                                 dest="repository_action")
        repository_subparsers.add_parser('list', help="List your repositories")

        r_create_sub = repository_subparsers.add_parser('create', help="Create a repository")
        r_create_sub.add_argument('--name', type=str, required=True, help="Repository name")
        r_create_sub.add_argument('--description', type=str, required=True, help="Repository description")

        r_remove_sub = repository_subparsers.add_parser('remove', help="Remove a repository")
        r_remove_sub.add_argument('--name', type=str, required=True, help="Repository name")

        r_info_sub = repository_subparsers.add_parser('info', help="Get information from a repository")
        r_info_sub.add_argument('--name', type=str, required=True, help="Repository name")

        r_getacl_sub = repository_subparsers.add_parser('getacl', help="Get ACL of a repository")
        r_getacl_sub.add_argument('--name', type=str, required=True, help="Repository name")

        r_setacl_sub = repository_subparsers.add_parser('setacl', help="Set ACL of a repository")
        r_setacl_sub.add_argument('--name', type=str, required=True, help="Repository name")
        r_setacl_sub.add_argument('--user', type=str, required=True, help="User you want to (un)grant")
        r_setacl_sub.add_argument('--acl', type=str, required=True, help="Repository acl (e.q: 'rw' or 'r', 'arw')")

        args = parser.parse_args(argv)

        if args.command == "repositories":
            if args.repository_action == "create":
                RepositoryApi.create(args.username, args.password, args.name, args.description)
                print("Repository '{}' Created !".format(args.name))

            if args.repository_action == "list":
                repositories = RepositoryApi.list(args.username, args.password)
                for repository in repositories:
                    print("{:40s} -> {}".format(repository.name, repository.uuid))

            if args.repository_action == "remove":
                RepositoryApi.remove(args.username, args.password, args.name)
                print("Repository '{}' Removed !".format(args.name))
                return

            if args.repository_action == "info":
                repository = RepositoryApi.get_info(args.username, args.password, args.name)
                print("Name:        '{}':".format(repository.name))
                print("Description: '{}'".format(repository.description))
                print("UUID:        '{}'".format(repository.uuid))
                print("Public:      '{}'".format(repository.public))
                print("URL:         '{}'".format(repository.url))
                print("Created at:  '{}'".format(repository.creation_time))
                return

            if args.repository_action == "getacl":
                acl = RepositoryApi.get_acl(args.username, args.password, args.name)
                for user in acl:
                    print("{:40s} -> {}".format(
                        user,
                        acl.get(user, '')
                    ))
                return

            if args.repository_action == "setacl":
                RepositoryApi.set_acl(args.username, args.password, args.name, args.user, args.acl)
                print("ACL applied to repository '{}' !".format(args.name))
                return

        if args.command == "sshkeys":
            if args.sshkey_action == "list":
                sshkeys = SSHKeyApi.list(args.username, args.password)
                for sshkey in sshkeys:
                    print("{:30s} -> {}".format(sshkey.name, sshkey.value))
                return
            if args.sshkey_action == "add":
                SSHKeyApi.add(args.username, args.password, args.value)
                print("SSH Key Added!")
            if args.sshkey_action == "remove":
                SSHKeyApi.remove(args.username, args.password, args.name)
                print("SSH Key Removed!")


def main():
    BlihCLI.cli(sys.argv[1:])
