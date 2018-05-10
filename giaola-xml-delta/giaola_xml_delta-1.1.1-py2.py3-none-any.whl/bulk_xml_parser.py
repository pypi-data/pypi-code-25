#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Created by Marsel Tzatzo on 05/12/2017.
"""
from giaola_xml_utils import XMLParser

class BulkXMLParser(XMLParser):
    def __init__(self, source, tag, bulk_count=100):
        super(BulkXMLParser, self).__init__(source, tag)
        self.bulk_count = bulk_count

    def __iter__(self):
        items = []
        for item in super(BulkXMLParser, self).__iter__():
            items.append(item)
            if len(items) == self.bulk_count:
                yield items
                items = []
        yield items
