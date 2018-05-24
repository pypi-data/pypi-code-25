#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 07/02/2018 17:50
# @Author  : Liozza
# @Site    : 
# @File    : git
# @Software: PyCharm
import subprocess


class GitHandler(object):
    def __init__(self, git_remote_branch='master'):
        self.__branch = git_remote_branch

    def git_pull(self):

        subprocess.check_output("git fetch --all", stderr=subprocess.STDOUT, shell=True)

        subprocess.check_output("git pull origin %s" % self.__branch, stderr=subprocess.STDOUT, shell=True)

    def git_force_sync_from_remote(self):

        subprocess.check_output("git fetch --all", stderr=subprocess.STDOUT, shell=True)

        subprocess.check_output("git reset --hard origin/%s" % self.__branch, stderr=subprocess.STDOUT, shell=True)

        subprocess.check_output("git pull origin %s" % self.__branch, stderr=subprocess.STDOUT, shell=True)

    def git_commit(self, **kwargs):
        commit_msg = ''
        # print("which file is changed")
        subprocess.check_output("git diff --stat", stderr=subprocess.STDOUT, shell=True)
        # change_file = subprocess.check_output("git diff --stat", stderr=subprocess.STDOUT, shell=True)
        # print("change file is: %s" % change_file)
        # print("check if changes")
        diff_status = subprocess.call("git diff --quiet", stderr=subprocess.STDOUT, shell=True)
        # print("diff_status: %s" % diff_status)
        if diff_status:
            for key, value in kwargs.items():
                commit_msg += """
                    %s: %s
                    """ % (key, value)

            print "Update details: %s" % commit_msg
            subprocess.check_output("git commit -a -m \"%s\" " % commit_msg, stderr=subprocess.STDOUT, shell=True)

            subprocess.check_output("git push origin HEAD:%s" % self.__branch, stderr=subprocess.STDOUT, shell=True)

        else:
            print "[INFO] No any changes."
