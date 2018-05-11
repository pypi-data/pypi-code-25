import sys
import argparse
from pathlib import Path
from subprocess import *
import re, platform, os

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='a subcommand')
    init_parser = subparsers.add_parser('init', help='initialize ipfs and add the save hook to the jupyter config file')
    init_parser.set_defaults(func=init)
    launch_parser = subparsers.add_parser('launch', help='create an environment for and launch a jupyter notebook')
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        parsed = parser.parse_args()
        parsed.func(parsed)
        
def init(parsed_args):
    config = Path.home() / '.jupyter' / 'jupyter_notebook_config.py'
    if not config.is_file():
        print("generating an empty jupyter config file")
        run(["jupyter", "notebook", "--generate-config"], encoding = 'utf-8', shell = False)
    with open(config, 'r') as file:
        contents = file.read()
        
    if "nyptune" in contents:
        print("jupyter config file already mentions nyptune")
    else:
        with open(config, "a") as file:
            print("appending nyptune pre-save-hook to jupyter config")
            file.write("\nfrom nyptune.jupyter import presave\nc.ContentsManager.pre_save_hook = presave\n")
    if "64" in platform.machine():
        machine = "amd64"
    else:
        machine = "386"
    name = platform.system().lower()
    ipfs = Path(os.path.realpath(__file__)).parent / "ipfs" / (name + "-" + machine) / "ipfs"
    run([str(ipfs), "init"], encoding = 'utf-8', shell = False)
    run([str(ipfs), "config", "--json", "Experimental.FilestoreEnabled", "true"], encoding = 'utf-8', shell = False)