#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function


from collections import OrderedDict


def tabdelim_to_dict(text, reverse=False):
    tups = [lx.strip().split() for lx in text.splitlines()]
    if reverse:
        tups = [tu[::-1] for tu in tups]
    return OrderedDict(tups)


