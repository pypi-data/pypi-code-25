#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2016-2018 Cyril Desjouy <ipselium@free.fr>
#
# This file is part of hwinfo
#
# hwinfo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hwinfo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hwinfo. If not, see <http://www.gnu.org/licenses/>.
#
#
# Creation Date : jeu. 19 avril 2018 10:20:20 CEST
# Last Modified : jeu. 19 avril 2018 10:48:28 CEST
"""
-----------
DOCSTRING

@author: Cyril Desjouy
"""

import re


class cpuinfo:

    def __init__(self):

        with open("/proc/cpuinfo", 'r') as f:
            self.cpu = f.read()

    @property
    def cache(self):

        _cache = re.compile('.*cache size.*')
        _cache = list(set(_cache.findall(self.cpu)))

        return _cache[0].split(':')[1].lstrip()

    @property
    def model(self):

        _model = re.compile('.*model name.*')
        _model = list(set(_model.findall(self.cpu)))

        return _model[0].split(':')[1].lstrip()

    @property
    def count(self):

        _count = re.compile('.*cache size.*')

        return len(_count.findall(self.cpu))

    def __str__(self):
        return '{} | Cache : {} | Threads : {}'.format(self.model, self.cache, self.count)
