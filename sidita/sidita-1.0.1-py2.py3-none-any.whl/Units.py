####################################################################################################
#
# sidita - Simple Distributed Task Queue
# Copyright (C) 2018 Fabrice Salvaire
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
#
####################################################################################################

"""Implements some units like duration and byte.

See also :mod:`datetime.timedelta` for duration.

Example of usage::

    size = 10@u_MB

    size * 2
    2 * size

    int(size)
    str(size)

"""

####################################################################################################

__all__ = [
    'u_Byte',
    'u_kB',
    'u_MB',
    'u_GB',
    'u_TB',
    'u_PB',
    'to_MB',

    'Duration',
    'u_s',
    'u_min',
    'u_hour',
    'u_day',
]

####################################################################################################

class IntUnit:

    ##############################################

    def __init__(self, value):
        self._value = value

    ##############################################

    def __int__(self):
        return int(self._value)

    ##############################################

    def __str__(self):
        return str(self._value)

    ##############################################

    def __mul__(self, other):
        return self.__class__(int(self) * int(other))

    ##############################################

    def __rmatmul__(self, other):
        return self.__mul__(other)

    ##############################################

    def __imul__(self, other):
        self._value *= int(other)
        return self

    ##############################################

    def __rmul__(self, other):
        return self.__mul__(other)

    ##############################################

    def __truediv__(self, other):
        return int(self) / int(other)

####################################################################################################

class FloatUnit(IntUnit):

    ##############################################

    def __float__(self):
        return float(self._value)

    ##############################################

    def __mul__(self, other):
        return self.__class__(float(self) * float(other))

    ##############################################

    def __imul__(self, other):
        self._value *= float(other)
        return self

    ##############################################

    def __truediv__(self, other):
        return float(self) / float(other)

####################################################################################################

class ByteSize(IntUnit):
    pass

u_Byte = ByteSize(1)
u_kB = u_Byte * 1024
u_MB = u_kB * 1024
u_GB = u_MB * 1024
u_TB = u_GB * 1024
u_PB = u_TB * 1024

def to_MB(x):
    return ByteSize(x) / u_MB

####################################################################################################

class Duration(FloatUnit):
    pass

u_s = Duration(1)
u_min = u_s * 60
u_hour = u_min * 60
u_day = u_hour * 24
