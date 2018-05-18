# Copyright 2018 Mingyi Zhang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, unicode_literals, print_function

import argparse
import os.path
import copy
import math

from cam.utils import console, shell
from cam.builder.build import Build
from cam.errors import FatalError
from cam.builder.configuration import  Load

def _Print(builds):
    for build in builds:
        console.log('')
        console.log( console.Back.BLUE + '    %-36s'%build.name)
        if not build.success and not build.failure:
            for step in build.config.steps:
                console.log( console.Fore.YELLOW + '  [ PEND ]' + console.Style.RESET_ALL
                + '    %-36s'%step)
        else:
            for step in build.config.steps:
                if step in build.success:
                    console.log( console.Fore.GREEN + '  [  OK  ]' + console.Style.RESET_ALL
                    + '    %-36s'%step)
                elif step == build.failure:
                    console.log( console.Fore.RED + '  [ FAIL ]' + console.Style.RESET_ALL
                    + '    %-36s'%build.failure)
                else:
                    console.log( console.Fore.YELLOW + '  [ PEND ]' + console.Style.RESET_ALL
                    + '    %-36s'%step)
                   
                

def _enviroment_init():
    powershell = shell.which('powershell')
    ComSpec = os.environ.get('ComSpec')

    PATH = os.environ.get('SystemRoot')
    PATH += ';' + os.path.dirname(ComSpec)
    PATH += ';' + os.path.dirname(powershell)

    for tool in ['git','cmake']:
        path = shell.which(tool)
        if tool is None:
            raise FatalError('No %s,please install it and add to PATH.')
        PATH = os.path.dirname(path) +';' +PATH

    os.environ['PATH']=PATH


def build(args):
    _enviroment_init()

    filename = args.file
    if filename is None:
        if os.path.isfile('./build.yml'):
            filename = './build.yml'
        else:
            if not os.path.exists('CMakeLists.txt') and \
               not os.path.exists('binding.gyp'):
               raise FatalError('default config file build.yml not exists.')    
    else:
        if not os.path.isfile(filename):
            raise FatalError('config file %s not exists.'%filename)    
    
    builds =[]
    projects = Load(filename, args.set )
    for project in projects:
        if args.debug:
            project.DEBUG = True
        if args.project is None or project.name in args.project :
            builds.append( Build(project,args ) )
    
    e = None

    try:
        for build in builds:
            build.run()
    except FatalError as e:        
        raise FatalError(e)
    except Exception as e:
        raise FatalError(e)
    finally:
        _Print(builds)
    return

def main(args):
    parser = argparse.ArgumentParser(prog="cam build")

    parser.add_argument(
        "--fetch",
        action='store_true',
        default=False,
        help="Fetch project build resource. ",
    )

    parser.add_argument(
        "--configure",
        action='store_true',
        default=False,
        help="Do configure for specifed project. ",
    )
    parser.add_argument(
        "--make",
        action='store_true',
        default=False,
        help="Do make for specifed project. ",
    )
    parser.add_argument(
        "--test",
        action='store_true',
        default=False,
        help="Do test for specifed project. ",
    )
    parser.add_argument(
        "--install",
        action='store_true',
        default=False,
        help="Do installation for specifed project. ",
    )
    parser.add_argument(
        "--cpplint",
        action='store_true',
        default=False,
        help="Do cpplint check for specifed project. ",
    )

    parser.add_argument(
        "--clean",
        action='store_true',
        default=False,
        help="Do clean specifed project. ",
    )

    parser.add_argument(
        "--package",
        action='store_true',
        default=False,
        help="Do package for specifed project. ",
    )


    
    parser.add_argument(
        "--set",
        type=str, action = 'append',
        help ="Set the specified var to replace config file( general part)."
    )

    parser.add_argument(
        '-p',"--project",
        type=str, action = 'append',
        help ="Only build the specified project"
        "If not set, build all projects"
    )

    parser.add_argument(
        "--log-dir",
        type=str, default=None,
        help ="Directory of the buid message writen to."
        "If not specified, message output to stdout.",
    )

    parser.add_argument(
        "--file",
        type=str, default=None,
        help ="Configuration file the build (build.yml by default)."
    )

    parser.add_argument(
        "--debug",
        action='store_true', default=False,
        help ="Build debug version or not."
    )

    parser.add_argument(
        "--verbose",
        action='store_true', default=False,
        help ="Print verbose."
    )



    args = parser.parse_args(args)

    if args.clean and ( args.fetch or
        args.configure or args.make or
        args.install or args.test or
        args.cpplint or args.package):
        raise FatalError('clean could not work with other options.')

    # Call the register function with the args from the command line
    build(args)
