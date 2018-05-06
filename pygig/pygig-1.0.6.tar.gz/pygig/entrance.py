#import net
import argparse
import os
from pygig import file_tool as ft


os.environ["GIT_PYTHON_REFRESH"] = "quiet"
import git

gitExePath = 'D:\\Git\\Git\\bin\\git.exe'

def listFile(searchStr = None):
    """
    get all .gitignore files if searchStr is None
    get specific .gitignore files including searchStr if searchStr is not None
    """
    # map = net.getFileUrlMap()
    map = ft.getFilePathMap()
    if searchStr is None:
        return '\n'.join(map.keys())
    else:
        return '\n'.join([x for x in map.keys() if x.lower().find(searchStr.lower()) != -1])

def showFile(fileName):
    """show the content of given .gitignore file"""
    # map = net.getFileUrlMap()
    map = ft.getFilePathMap()
    lowerKeyMap = {}
    for key in map:
        lowerKeyMap[key.lower()] = map[key]
    # print(net.getFileContent(map[fileName.strip().lower()]))
    print(ft.getFileContent(lowerKeyMap[fileName.strip().lower()]))

def genFile(fileNames, path):
    """generate .gitignore files in fileNames at path"""
    #map = net.getFileUrlMap()
    map = ft.getFilePathMap()
    lowerKeyMap = {}
    for key in map:
        lowerKeyMap[key.lower()] = map[key]
    content = []
    for fileName in fileNames:
        # content.append(net.getFileContent(map[fileName.strip()]))
        content.append(ft.getFileContent(lowerKeyMap[fileName.strip().lower()]))
    with open(os.path.join(path,'.gitignore'), 'w', newline='') as fw:
        fw.write('\n\n'.join(content))

def updateIgnoreFiles():
    git.refresh(gitExePath)
    repo = git.Repo(os.path.join(os.path.abspath(__file__),'..','..','gitignore'))
    remote = repo.remote()
    remote.pull()

def entrance():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='command', metavar='command')
    sub_parsers.required = True
    sub_parser = sub_parsers.add_parser('list',
                                        help='list all .gitignore file can be generated for you')
    sub_parser.add_argument("-s", "--search", help="search .gitignore files including these words")
    sub_parser = sub_parsers.add_parser('show',
                                        help='show the content of given .gitignore file')
    sub_parser.add_argument("name", help=".gitignore file name")
    sub_parser = sub_parsers.add_parser('gen',
                                        help='generate .gitignore files')
    sub_parser.add_argument("fileNames", help=".gitignore files' name")
    sub_parser.add_argument("-p", "--path", default='.', help="the directory to generate .gitignore file")
    sub_parser = sub_parsers.add_parser('update',
                                        help='update gitignore directory')
    args = parser.parse_args()
    if args.command == 'list':
        print(listFile(args.search))
    elif args.command == 'show':
        if args.name is None:
            print('please input .gitignore file name')
        else:
            showFile(args.name)
    elif args.command == 'gen':
        fileNames = args.fileNames.split(',')
        genFile(fileNames, args.path)
    elif args.command == 'update':
        updateIgnoreFiles()

