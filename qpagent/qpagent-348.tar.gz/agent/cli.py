#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.cli
    ~~~~~~~~~~~~

    This module is the main of agent.

    :copyright: (c) 2017 by Ma Fei.
"""
import os
import logging

import click

logger = logging.getLogger(__name__)

plugin_folder = os.path.join(os.path.dirname(__file__), 'cmds')


class CLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns[name]


@click.command(cls=CLI)
def qa():
    pass


def main():
    print("A Terminal Tools For Agent")
    qa()


if __name__ == "__main__":
    main()
