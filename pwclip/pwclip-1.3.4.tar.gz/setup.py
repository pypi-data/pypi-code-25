# -*- coding: utf-8 -*-
"""
Generic Setup script, takes package info from __pkginfo__.py file.
"""
from sys import argv
from os import listdir, chdir, getcwd, path
from setuptools import setup, find_packages

__docformat__ = "restructuredtext en"

def packages(directory):
    """return a list of subpackages for the given directory"""
    result = []
    for package in listdir(directory):
        absfile = path.join(directory, package, '__init__.py')
        if path.exists(absfile):
            result.append(path.dirname(absfile))
            result += packages(path.dirname(absfile))
    return result

def scripts(linux_scripts):
    """creates the proper script names required for each platform"""
    from distutils import util
    if util.get_platform()[:3] == 'win':
        return linux_scripts + [script + '.bat' for script in linux_scripts]
    return linux_scripts

if __name__ == '__main__':
    kwargs = {}
    kwargs['packages'] = ['pwclip'] + packages('pwclip')
    with open(path.join('pwclip', '__pkginfo__.py'), 'r') as f:
        __pkginfo = f.read()
        exec(__pkginfo, kwargs)
    if '--pybuilder' in argv:
        print()
        for (k, v) in sorted(kwargs.items()):
            print('%s = %s'%(k, v))
        print()
        if 'version' in kwargs.keys():
            if '%s (current)'%kwargs['version'] not in kwargs['long_description']:
                print('\033[31mWARNING: no current changelog found ' \
                    'for version \033[33m%s\033[0m'%kwargs['version'])
        input('press Enter to continue...')
        del argv[argv.index('--pybuilder')]
    print(kwargs)
    setup(**kwargs)
