#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Geo Tools
Copyright (C) 2018  Pedro Rodrigues <prodrigues1990@gmail.com>

This file is part of Geo Tools.

Geo Tools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2 of the License.

Geo Tools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Geo Tools.  If not, see <http://www.gnu.org/licenses/>.
"""

def dms2dd(direction, degrees, minutes, seconds):
    """Converts a latitude or longitude from DMS to decimal degrees notation

    Consider the following coordinate:

        N038.57.38.000
        W009.11.04.000

    >>> from geo_tools import dms2dd
    >>> (dms2dd('N', 38.0, 57.0, 38.0), dms2dd('W', 9.0, 11.0, 4.0))
    (38.96055555555556, -9.184444444444445)

    Args:
        direction   (string): The coordinate hemisphere; 'N', 'E', 'S', or 'W'
        degrees     (float): Degrees deviation
        minutes     (float): Minutes deviation
        seconds     (float): Seconds deviation

    Returns:
        float: the DMS coordinate latitude or longitude in decimal degrees
        notation
    """
    decimal_degrees = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)
    direction = direction.upper()
    if direction == 'S' or direction == 'W':
        decimal_degrees *= -1
    return decimal_degrees
