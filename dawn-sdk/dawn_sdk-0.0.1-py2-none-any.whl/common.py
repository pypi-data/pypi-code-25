# -*- coding: utf-8 -*-

import logging

def get_value(value, default_value):
  if value is None:
    return default_value

  return value

# 连接超时，单位秒
connect_timeout = 30

logger = logging.getLogger()

def get_logger():
  return logger