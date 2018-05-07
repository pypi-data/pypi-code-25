#!/usr/bin/env python

# encoding: utf-8

'''
 * Create File logger
 * Created by leixu on 2018/4/23
 * IDE PyCharm
'''

import logging
import sys

import logging

logger = logging.getLogger("RetryMe")

formatter = logging.Formatter('%(asctime)s %(module)s %(lineno)d %(levelname)-8s: %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  # 也可以直接给formatter赋值
console_handler.setLevel(logging.WARN)

logger.addHandler(console_handler)
