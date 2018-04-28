#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bibtexparser
import re
from pypinyin import pinyin, Style


def to_pinyin(string):
    return ' '.join(sum(pinyin(string, style=Style.TONE3), []))


def if_containing_chinese(test_string):
    return bool(re.findall(r'[\u4e00-\u9fff]+', test_string))


def add_pinyin_key_to_bib_database(db):
    for entry in db.entries:
        if if_containing_chinese(entry["author"]):
            entry["key"] = to_pinyin(entry["author"])
    return db


def add_pinyin_key_to_bib_file(input_bib, output_bib):
    with open(input_bib, encoding="utf-8") as input_file:
        bib_database = bibtexparser.load(input_file)

    writer = bibtexparser.bwriter.BibTexWriter()
    with open(output_bib, encoding="utf-8", mode="w") as output_file:
        output_file.write(writer.write(add_pinyin_key_to_bib_database(bib_database)))
