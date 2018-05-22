# -*- coding: utf-8 -*-

import os
import pathspec
import argparse
import json
from ftplib import FTP
import ftplib

from . import json_cleaner

# TODO: filefliter can be optimized.
# OPTIMIZE
def listAllfile(rootdir):
    fileList = list()
    list_dirs = os.walk(rootdir)
    for root, dirs, files in list_dirs:
        for file in files:
            fileList.append(os.path.join(root, file))
    return fileList

def file_filter(file_list, ignore_files):
    fileSet = set(file_list)
    spec = getSpec(ignore_files)
    fileSet = fileSet.difference(set(spec.match_files(fileSet)))
    return list(fileSet)

def isMatchSpec(s ,spec):
    if len(set(spec.match_files([s]))) is 0:
        return False
    else:
        return True

def getSpec(files):
    text = str()
    for file in files:
        if not os.path.exists(file):
            print('Can\'t find file '+file+'.')
        else:
            with open(file) as fh:
                text = text + '\n' + fh.read()
    spec = pathspec.PathSpec.from_lines(pathspec.GitIgnorePattern, text.splitlines())
    return spec

def getConfig(file):
    if not os.path.exists(file):
        raise FileNotFoundError('Can\'t find config file \'.ftpbackup\'')
    else:
        with open(file, 'r', encoding='UTF-8') as fh:
            confText = json_cleaner.remove_comments(fh.read())
        return json.loads(confText)

def walkAndUpload(ftp, remote, rootdir, ignore_files):
    fileList = list()
    spec = getSpec(ignore_files)

    list_dirs = os.walk(rootdir)
    for root, dirs, files in list_dirs:
        if not isMatchSpec(root+'\\', spec):
            # print('root = ' + root)
            # print('remote = ' + (remote + root[1:len(root)].replace('\\', '/')))
            remotedir = remote + root[1:len(root)].replace('\\', '/')
            ftp.cwd(remotedir)
            print('enter dir: "' + remotedir + '"')
            for dir in dirs:
                if not isMatchSpec(dir+'\\', spec):
                    # print('  - dir = ' + dir)
                    print('try to make dir "' + dir + '"... ', end='')
                    try:
                        ftp.mkd(dir)
                    except UnicodeDecodeError as e:
                        pass
                    except ftplib.error_perm :
                        pass
                    print('Complete!')
            for file in files:
                # print('  - file = ' + file)
                print('upload file "' + os.path.join(root, file) + '"... ', end='')
                with open(os.path.join(root, file), 'rb') as fp:
                    ftp.storbinary('STOR '+file, fp, blocksize=8192, callback=None, rest=None)
                print('Complete!')

def subGenConf(args):
    file = args.file
    isExist = os.path.exists(file)
    print(isExist)
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
    text = """{
    "protocol": "ftp",
    "host": "localhost", // string - The hostname or IP address of the FTP server. Default: 'localhost'
    "port": 21, // integer - The port of the FTP server. Default: 21
    "user": "anonymous", // string - Username for authentication. Default: 'anonymous'
    "pass": "anonymous@", // string - Password for authentication. Default: 'anonymous@'
    "encoding": "big5",
    "remote": ".",
    "local": ".",
    "useGitIgnore": true,
    "gitIgnoreEncoding": "utf-8",
    "useFtpIgnore": true,
    "ftpIgnoreEncoding": "utf-8"
}
    """
    with open(file, 'w', encoding='UTF-8') as fp:
        fp.write(text)

def subBackup(args):
    config = getConfig(args.configfile)

    ftp = FTP()
    ftp.encoding = config['encoding']
    ftp.connect(config['host'], config['port'])
    ftp.login(config['user'], config['pass'])

    igFiles = []
    if config['useGitIgnore']:
        igFiles += ['.gitignore']
    if config['useFtpIgnore']:
        igFiles += ['.ftpignore']
    walkAndUpload(ftp, config['remote'],config['local'],igFiles)


def argHandle():
    parser = argparse.ArgumentParser(description='Backup to FTP.')
    subparsers = parser.add_subparsers(title='subcommands',
                                        description='valid subcommands',
                                        help='additional help',
                                        dest='subparser_name')

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
