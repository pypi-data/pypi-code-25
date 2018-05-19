from __future__ import print_function
from builtins import str

import os
import sys

import hcl


def terragrunt_source():  # type: () -> str
    root = os.environ['TERRAGRUNT_DEFAULT_MODULES_REPO']

    try:  # Python 2.x
        root = root.decode('utf8')  # type: ignore
    except AttributeError:  # Python 3.x
        pass

    with open('terraform.tfvars', 'r') as fp:
        tfvars = hcl.load(fp)

    source = tfvars['terragrunt']['terraform']['source']
    path = source.split('//')[1].split('?')[0]

    return root + '//' + path


def error(code, mesg):  # type: (int, str) -> None
    print(str(mesg), file=sys.stderr)
    exit(code)


def main():  # type: () -> None
    try:
        print(terragrunt_source())
    except IOError as e:
        error(2, str(e))
    except KeyError as e:
        error(3, 'Environment variable TERRAGRUNT_DEFAULT_MODULES_REPO '
                 'is undefined!')

    exit(0)
