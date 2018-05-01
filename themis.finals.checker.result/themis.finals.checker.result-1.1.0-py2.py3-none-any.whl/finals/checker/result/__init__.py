# -*- coding: utf-8 -*-
from __future__ import absolute_import
from enum import Enum


class Result(Enum):
    UP = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    INTERNAL_ERROR = 110
