#!/usr/bin/env python3

import os
import sys
import argparse

res = {
    'c': 'controllers',
    'd': 'demo',
    'da': 'data',
    'r': 'report',
    's': 'security',
    'st': 'static',
    't': 'tests',
    'w': 'wizard',
}


def create_files(location, models=True, common=False):
    if models:
        files = ('__init__.py', '__manifest__.py') \
            if common else ('__init__.py', 'models.py')
    else:
        files = ('views.xml', )

    for name in files:
        content = "# -*- coding: utf-8 -*-\n" \
            if '.py' in name else \
            "<?xml version='1.0' encoding='utf-8'?>\n<odoo>\n\n</odoo>\n"
        if "init" in name:
            content += "\nfrom . import models\n"
            args = sys.argv[-1]
            for arg in filter(
                    lambda arg: arg in ('r', 'w', 'c'), args.split(",")):
                content += "from . import {0}\n".format(res[arg])
        f = open(os.path.join(location, name), 'w')
        f.write(content)
        f.close()


def create_similar_files(module_name, folder, init=False):
    try:
        content = "# -*- coding: utf-8 -*-"
        if init:
            content += "\n\nfrom . import {0}\n".format(folder)
            path = os.path.join(module_name + "/" + folder, "__init__.py")
        else:
            path = os.path.join(module_name + "/" + folder, folder + ".py")
        f = open(path, 'w')
        f.write(content)
        f.close()
    except OSError:
        print("Oops... Something bad happened... -_-")


def create_similar(module_name, folder):
    try:
        location = module_name + "/" + folder
        os.makedirs(location)
        create_similar_files(module_name, folder)
        create_similar_files(module_name, folder, init=True)
    except OSError:
        print("Oops... Something bad happened -_-")


def create_dirs(args):
    module_name, includes = args.name, args.includes
    if includes:
        all_folders = [res[folder] for folder in includes.split(',')
                       if folder in res]
        for folder in all_folders:
            try:
                if folder in ('report', 'wizard', 'tests', 'controllers'):
                    create_similar(module_name, folder)
                else:
                    os.makedirs(module_name + "/" + folder)
            except OSError:
                print("Oops... Something bad happened... -_-")
    try:
        os.makedirs(module_name + "/models")
        os.makedirs(module_name + "/views")
        create_files(module_name, common=True)
        create_files(module_name + "/models")
        create_files(module_name + "/views", models=False)
    except OSError:
        print("'{0}' directory already exists!".format(module_name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--name", help="Name of the module", required="True")
    parser.add_argument(
        "-i", "--includes",
        help='''Comma separated chars of folder names... i.e.
            c => controllers,
            d => demo,
            da => data,
            r => report,
            s => security,
            st => static,
            t => tests,
            w => wizard''')
    args = parser.parse_args()
    create_dirs(args)
