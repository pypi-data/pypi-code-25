# -*- coding: utf-8 -*-
import os

__version__ = '0.0.1'

# 准备好文件夹
USER_HOME = os.path.expanduser('~')
PATH = os.path.join(USER_HOME, ".debug_a")
LOG_DIR = os.path.join(USER_HOME, ".debug_a/log/")
DATA_DIR = os.path.join(USER_HOME, ".debug_a/data/")
if not os.path.exists(PATH):
    os.mkdir(PATH)
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)


# API 提升

from debug_a.utils import print_constitutions

