# -*- coding: utf-8 -*-
#
# __main__.py
#
# Author:   Toke Høiland-Jørgensen (toke@toke.dk)
# Date:     21 May 2015
# Copyright (c) 2015-2016, Toke Høiland-Jørgensen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from multiprocessing import freeze_support

from flent import run_flent

if __name__ == "__main__":
    freeze_support()
    sys.exit(run_flent())
