#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 09/04/2018 17:08
# @Author  : Zhang Lei
# @Site    : 
# @File    : version
# @Software: PyCharm

# __version__ = '1.0.0'
# __release_date = ''
# __release_log__ = '''
# Create ops common libraries, Beta
# '''

__version__ = '1.3.0'
__release_date = '2018-04-09'
__release_log__ = '''
Production, support custom remote branch for git module
Usage:
    gitlab = GitHandler(git_remote_branch='dev')
    gitlab.git_pull()
'''