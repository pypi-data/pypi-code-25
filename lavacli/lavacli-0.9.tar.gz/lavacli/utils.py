# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2017 Rémi Duraffort
# This file is part of lavacli.
#
# lavacli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lavacli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lavacli.  If not, see <http://www.gnu.org/licenses/>

import re


def print_u(string):
    try:
        print(string)
    except UnicodeEncodeError:
        print(string.encode("ascii", errors="replace").decode("ascii"))


(VERSION_2017_11,
 VERSION_2017_12,
 VERSION_2018_1,
 VERSION_2018_2,
 VERSION_LATEST) = range(5)

VERSIONS = {
    "2017.11": VERSION_2017_11,
    "2017.12": VERSION_2017_12,
    "2018.1": VERSION_2018_1,
    "2018.2": VERSION_2018_2
}


def parse_version(version):
    pattern = re.compile(r"(?P<version>20\d{2}\.\d{1,2})")
    if not isinstance(version, str):
        version = str(version)
    m = pattern.match(version)
    if m is None:
        return None
    return VERSIONS.get(m.groupdict()["version"], VERSION_LATEST)
