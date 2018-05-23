"""
Main module for hostblock command line utility.
"""
import argcomplete
import argparse
import json
import os
import pkg_resources
import re
import subprocess
import sys
import textwrap
import hostblock.hosts

global config_path

class BlockedHosts(set):
    '''Extensible set of hosts.'''

    def __init__(self, hosts = set(), redirect = '0.0.0.0'):
        self.redirect = redirect
        self.update(hosts)
        self.re = re.compile('^\s*((([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]))\s*(\#.*)?')
        super()

    def __iter__(self):
        ordered_hosts = list(set(self))
        ordered_hosts.sort()
        for x in ordered_hosts:
            yield x
        
    def __repr__(self):
        return "BlockedHosts('{}', {})".format(set(self), self.redirect)

    def __str__(self):
        delimiter = '\n{} '.format(self.redirect)
        return delimiter + delimiter.join(list(self))

    def __add__(self, other):
        return BlockedHosts(set(self).union(set(other)), self.redirect)

    def __iadd__(self, other):
        self.update(other)
        return self

    def __sub__(self, other):
        return BlockedHosts(set(self).difference(set(other)), self.redirect)

    def __isub__(self, other):
        self.difference_update(other)
        return self
        
    def load(self, hosts_data:str):
        for line in hosts_data.split('\n'):
            found_host = self.re.match(line)
            if found_host is not None:
                self.add(found_host.groups()[0])


def __parse_args():
    """Parse command line arguments and return an argparse object."""
    parser = argparse.ArgumentParser(
        prog = "hostblock",
        description="Add hosts file entries to block unwanted hosts.",
        )
    parser.add_argument(
        "-v", "--version", action="store_true",
        help="Show version info and exit."
        )
    parser.add_argument(
        "--config", action="store", type=str,
        help='''Specify config file path. Defaults to '~/.hostblock'.'''
        )
    parser.add_argument(
        "--hosts-file", action="store", type=str,
        help='''Specify hosts file path. Defaults to '/etc/hosts'.'''
        )
    subparsers = parser.add_subparsers(
        description="(use each command with -h for more help)",
        dest="cmd",
        )
    parser.set_defaults(
        config=os.path.expanduser('~/.hostblock'),
        hosts_file = '/etc/hosts',
        )

    parser_ab = subparsers.add_parser(
        "ab",
        description='''Add host(s) to local blacklist.''',
        )
    parser_rb = subparsers.add_parser(
        "rb",
        description='''Remove host(s) from local blacklist.''',
        )
    parser_cb = subparsers.add_parser(
        "cb",
        description='''Remove all hosts from local blacklist.''',
        )
    parser_lb = subparsers.add_parser(
        "lb",
        description='''List all hosts from local blacklist.''',
        )
    parser_aw = subparsers.add_parser(
        "aw",
        description='''Add host(s) to local whitelist.''',
        )
    parser_rw = subparsers.add_parser(
        "rw",
        description='''Remove host(s) from local whitelist.''',
        )
    parser_cw = subparsers.add_parser(
        "cw",
        description='''Remove all hosts from local whitelist.''',
        )
    parser_lw = subparsers.add_parser(
        "lw",
        description='''List all hosts from local whitelist.''',
        )
    parser_list = subparsers.add_parser(
        "list",
        description='''List all hosts that will be blocked.''',
        )
    parser_apply = subparsers.add_parser(
        "apply",
        description='''Apply blocked hosts to your hosts file.''',
        )
    hosts_argument = {
        }
    for subparser in [ parser_ab, parser_rb, parser_aw, parser_rw ]:
        subparser.add_argument(
            dest='hosts', metavar='host', type=str, nargs='+',
            help='''Hostname to add/remove from local blacklist/whitelist.''',
            )

    argcomplete.autocomplete(parser)
    return parser.parse_args()

def require_sudo(func):
    '''Call same script again with sudo and pass confing argument.'''
    def wrapper(*args, **kwargs):
        if os.geteuid() == 0:
            func(*args, **kwargs)
        else:
            print("Acquiring sudo permission.")
            script = sys.argv[0]
            rest_args = sys.argv[1:]
            config = config_path
            sp = subprocess.Popen(
                ['sudo', 'python3', script, '--config', config, *rest_args])
            sp.communicate()
            sys.exit(sp.returncode)
    return wrapper

@require_sudo
def update_hosts_file(hosts_file:str, blocked_hosts:BlockedHosts):
    host_re = re.compile(
        '^\s*({})\s.*$'.format(re.escape(blocked_hosts.redirect)))
    existing_no_block_lines = ''
    with open(hosts_file) as f:
        for line in f.readlines():
            found_host = host_re.match(line)
            if found_host is None:
                existing_no_block_lines += line
    if existing_no_block_lines[-1] == '\n':
        existing_no_block_lines = existing_no_block_lines[:-1]
    with open(hosts_file, 'w') as f:
        print('Updating ' + hosts_file)
        f.write(existing_no_block_lines + str(blocked_hosts))

def init_local_config():
    if not os.path.isfile(config_path):
        with open(config_path, 'w') as f:
            f.write('{ "whitelist":[], "blacklist":[] }')

def get_local_config():
    init_local_config()
    with open(config_path) as f:
        return json.loads(f.read())

def set_local_config(config:dict):
    with open(config_path, 'w') as f:
        f.write(json.dumps(config))

def add_to_local_config(set_blocked_hosts:BlockedHosts, which_list:str):
    config = get_local_config()
    blocked_hosts = BlockedHosts(set(config[which_list]))
    blocked_hosts += set_blocked_hosts
    config[which_list] = list(blocked_hosts)
    set_local_config(config)

def remove_from_local_config(set_blocked_hosts:BlockedHosts, which_list:str):
    config = get_local_config()
    blocked_hosts = BlockedHosts(set(config[which_list]))
    blocked_hosts -= set_blocked_hosts
    config[which_list] = list(blocked_hosts)
    set_local_config(config)

def clear_local_config(which_list:str):
    config = get_local_config()
    config[which_list] = []
    set_local_config(config)

def list_local_config(which_list:str):
    config = get_local_config()
    return config[which_list]

def get_default_hosts():
    blocked_hosts = BlockedHosts()
    all_resources = pkg_resources.resource_listdir("hostblock.hosts", '.')
    hosts_resources = [ s for s in all_resources if s.endswith(".hosts") ]
    for f in hosts_resources:
        hosts_data = pkg_resources.resource_string(
            "hostblock.hosts", f).decode("utf-8")
        blocked_hosts.load(hosts_data)
    return blocked_hosts

def main():
    global config_path
    args = __parse_args()
    config_path = args.config
    
    if args.version:
        print("hostblock {} - Copyright {} {} <{}>".format(
            hostblock.__version__,
            hostblock.__year__,
            hostblock.__author__,
            hostblock.__author_email__,
            ))
        sys.exit(0)

    if args.cmd == 'ab':
        add_to_local_config(BlockedHosts(set(args.hosts)), 'blacklist')
    if args.cmd == 'rb':
        remove_from_local_config(BlockedHosts(set(args.hosts)), 'blacklist')
    if args.cmd == 'cb':
        clear_local_config('blacklist')
    if args.cmd == 'lb':
        print('\n'.join(list_local_config('blacklist')))
    if args.cmd == 'aw':
        add_to_local_config(BlockedHosts(set(args.hosts)), 'whitelist')
    if args.cmd == 'rw':
        remove_from_local_config(BlockedHosts(set(args.hosts)), 'whitelist')
    if args.cmd == 'cw':
        clear_local_config('whitelist')
    if args.cmd == 'lw':
        print('\n'.join(list_local_config('whitelist')))
    if args.cmd == 'list':
        blocked_hosts = get_default_hosts()
        local_config = get_local_config()
        blocked_hosts += local_config['blacklist']
        blocked_hosts -= local_config['whitelist']
        print(blocked_hosts)
    if args.cmd == 'apply':
        blocked_hosts = get_default_hosts()
        local_config = get_local_config()
        blocked_hosts += local_config['blacklist']
        blocked_hosts -= local_config['whitelist']
        update_hosts_file(args.hosts_file, blocked_hosts)
    sys.exit(0)

if __name__ == "__main__":
    main()


