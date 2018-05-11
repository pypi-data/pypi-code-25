#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Created by Marsel Tzatzo on 05/12/2017.
"""
class Delta(object):
    def __init__(self):
        super(Delta, self).__init__()

    def diff(self, pk, old_data, new_data):
        old_data = { k.get(pk): k for k in old_data }
        new_data = { k.get(pk): k for k in new_data }

        to_update = {}
        to_create = {}

        for k, new in new_data.items():
            old = old_data.get(k)
            if not old:
                to_create[k] = new
            else:
                if not sorted(old.items()) == sorted(new.items()):
                    to_update[k] = new

        return to_create, to_update
