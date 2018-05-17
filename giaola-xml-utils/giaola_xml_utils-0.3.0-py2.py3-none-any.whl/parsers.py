#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Created by Marsel Tzatzo on 01/12/2017.
"""

from builtins import str as text

import lxml.etree as ET

import logging
logger = logging.getLogger(__name__)

class XMLParser(object):

    def __init__(self, source, tag, recover=True):
        self.source = source
        self.tag = tag
        self.recover = recover

    def __iter__(self):
        context = ET.iterparse(source=self.source,
                               events=('end',),
                               huge_tree=True,
                               recover=self.recover)
        iterator = iter(context)

        for event, elem in iterator:
            try:
                if elem.tag == self.tag:
                    element_dict = self.element_to_dict(elem)

                    elem.clear()

                    while elem.getprevious() is not None:
                        del elem.getparent()[0]

                    yield (element_dict)

            except Exception:
               logger.exception('parse')
        del context

    def element_to_dict(self, root):
        dict = {}
        children = root.getchildren()
        for child in children:
            if child.getchildren():
                if child.tag in dict:
                    if isinstance(dict[child.tag], list):
                        dict[child.tag].append(self.element_to_dict(child))
                    else:
                        dict[child.tag] = [dict[child.tag], self.element_to_dict(child)]
                else:
                    dict[child.tag] = self.element_to_dict(child)
            else:
                val = text(child.text) if child.text else None
                if val:
                    dict[child.tag] = text(val)
        return dict
