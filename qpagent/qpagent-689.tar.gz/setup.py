#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################
# File Name: setup.py
# Author: mafei
# Mail: fei.ma03@ele.me
# Created Time:  2017-06-26 01:25:34 AM
#############################################

from setuptools import setup, find_packages

import agent

setup(
    name="qpagent",
    version=agent.__version__,
    description="agent",
    long_description=open("README.md").read(),
    license="MIT Licence",

    author="mafei",
    author_email="fei.ma03@ele.me",
    url="https://git.elenet.me/waimaiqa/qualityplatform.agent.git",

    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    platforms="any",
    install_requires=["requests", "bottle", "click", "shutit", "enum34", "selenium", "apscheduler",
                      "raven", "bs4", "apptoolkit", "pexpect"],
    entry_points={
        'console_scripts': [
            'serve = agent.cmds.serve:serve',
        ]
    },
)
