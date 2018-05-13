import sys
import argparse

from vuray.api import VurayApi

# TODO: Check for requirements.txt
# TODO: Check for requirements[.-]*.txt or *[.-]requirements.txt
# TODO: Check for setup.py sections
# TODO: Check for current environment and all installed packages


def run(args=sys.argv[1:]):
    with VurayApi() as client:
        pass


if __name__ == '__main__':
    run()
