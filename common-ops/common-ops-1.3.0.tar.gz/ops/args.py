#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 07/02/2018 16:02
# @Author  : Liozza
# @Site    : 
# @File    : args
# @Software: PyCharm

import argparse
import textwrap
import sys

details = {}


class ArgsHandle(object):
    def __init__(self):
        pass

    def get_args(self):
        example_str = """
           EXAMPLES:
                python %s -p s-search-classification-solr -e release -r us-east-1 -t ecs
           RETURN VALUE FORMAT:
           {
                "project": "string",
                "region": "string",
                "tag": "string",
                "env": "string"
                "details": "{}"
           }    
            """ % __file__.split('/')[-1]

        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent(example_str))
        help = "Required, project name, e.g s-search-classification-solr"
        parser.add_argument('-p', '--project', metavar='project_name', help=help, required=True)
        help = "Required, project env parameter, prod|prod2|release|local"
        parser.add_argument('-e', '--env', metavar='project_environment',
                            choices=['release', 'prod2', 'prod', 'release2', 'ci', 'qa', 'dev'],
                            help=help, required=True, default="local")
        help = "Required, project region, us-east-1|cn-north-1"
        parser.add_argument('-r', '--region', metavar='project_region',
                            choices=['cn-north-1', 'us-east-1', 'local'],
                            help=help, required=True, default=None)
        help = "Required, project tag, ecs|rancher"
        parser.add_argument('-t', '--tag', metavar='project_tag', help=help, required=True, default=None)
        help = "Optional, project update details, image=test:dev.1.0"
        parser.add_argument('-d', '--details', action=type(b'', (argparse.Action,),
                                                          dict(__call__=lambda self, parser, namespace, values,
                                                                               option_string: getattr(namespace,self.dest).update(dict([v.split('=') for v in values.replace(';', ',').split(',') if
                                                                               len(v.split('=')) == 2])))), default={},
                            metavar='KEY1=VAL1,KEY2=VAL2;KEY3=VAL3...', help=help, required=False)
        help = "Git Sync Parameter"
        parser.add_argument('--sync', dest='git_flag', action='store_true', default=False, help=help)
        help = "Force Deploy Only for project Admin!"
        parser.add_argument('--force', dest='force_flag', action='store_true', default=False, help=help)

        args = parser.parse_args().__dict__
        for key, value in args.items():
            if len(sys.argv) < 2 or value == '':
                print "Parameter %s can not be empty!" % key
                parser.parse_args(['-h'])
        return args
