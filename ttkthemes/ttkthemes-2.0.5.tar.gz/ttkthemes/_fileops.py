"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2017-2018 RedFantom
"""
import os
import colorsys


def adjust_colors(file_name, hue=1.0, saturation=1.0, brightness=1.0):
    """Adjust the hex colors in a given file"""
    with open(file_name) as fi:
        lines = fi.readlines()
    for line in lines:
        pass


