# -*- coding: utf-8 -*-

import os
import pathspec
import argparse
import json
from ftplib import FTP
import ftplib

from . import json_cleaner
from . import Config, FtpBackup
from . import __DEFAULT_CONF__

def subGenConf(args):
    file = args.file
    isExist = os.path.exists(file)
    if not isExist:
        # TODO print something
        writeDefaultConf(file)
    elif isExist and args.force:
        # TODO print something
        writeDefaultConf(file)
    else:
        yn = input('File \'' + file + '\' is existing, '
            +'do you want to overwrite the existing file? (y/n): ')
        while yn != 'y' and yn != 'n':
            yn = input('plz input y or n : ')
        if yn == 'y':
            writeDefaultConf(file)
        else:
            pass

def writeDefaultConf(file):
    with open(file, 'w', encoding='UTF-8') as fp:
        fp.write(__DEFAULT_CONF__)

def subBackup(args):
    conf = Config(args.configfile)
    ftpBackup = FtpBackup(conf)
    ftpBackup.startBackup()

def argHandle():
    parser = argparse.ArgumentParser(description='Backup to FTP.')
    subparsers = parser.add_subparsers(
        title = 'commands',
        dest  = 'subparser_name'
    )
    subparsers.required = True

    parser_genconf = subparsers.add_parser(
        'genconf',
        description = 'Generate a default config file.'
    )
    parser_genconf.add_argument(
        '-F', '--force',
        action = 'store_true',
        help = 'overwrite the config file if it exists.'
    )
    parser_genconf.add_argument(
        '-f', '--file',
        action = 'store',
        default = '.ftpbackup',
        help = 'assign the config file to be writed, default is \'.ftpbackup\'.'
    )
    parser_genconf.set_defaults(func=subGenConf)

    parser_backup = subparsers.add_parser(
        'backup',
        description = 'Backup all the file in the \'local\' floder to \'remote\' on ftp. '+
                'You can change the config in config file(default is \'.ftpbackup\').'
    )
    parser_backup.add_argument(
        '-c', '--conf',
        dest = 'configfile',
        action = 'store',
        default = '.ftpbackup',
        help = 'assign the config file to be loaded, default is \'.ftpbackup\'.'
    )
    # TODO: add parameters below
    # parser_backup.add_argument('-F', '--force')
    # parser_backup.add_argument('-v', '--verbose')
    parser_backup.set_defaults(func=subBackup)
    args = parser.parse_args()
    return args

def run():
    args = argHandle()
    if args.subparser_name is None:
        print('ERROR: plz input a subcommands')
    else:
        args.func(args)

if __name__ == '__main__':
    run()
