from __future__ import print_function, unicode_literals

import os

import hcl


def main():
    try:  # Python 2.x
        root = os.environ['TERRAGRUNT_DEFAULT_MODULES_REPO'].decode('utf8')
    except AttributeError:  # Python 3.x
        root = os.environ['TERRAGRUNT_DEFAULT_MODULES_REPO']

    with open('terraform.tfvars', 'r') as fp:
        tfvars = hcl.load(fp)

    source = tfvars['terragrunt']['terraform']['source']
    path = source.split('//')[1].split('?')[0]

    print(root, '//', path, sep='')
    exit(0)
