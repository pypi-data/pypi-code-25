#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bibtexparser
from bibtexparser.bparser import BibTexParser
import re
from pypinyin import pinyin, Style


def to_pinyin(string):
    return ' '.join(sum(pinyin(string, style=Style.TONE3), []))


def if_containing_chinese(test_string):
    return bool(re.findall(r'[\u4e00-\u9fff]+', test_string))


def add_pinyin_key_to_bib_database(db):
    for entry in db.entries:
        try:
            if if_containing_chinese(entry["author"]):
                entry["key"] = to_pinyin(entry["author"])
        except KeyError:
            print("Entry dose not contain author info. Skip.")
            print(entry)
    return db


def add_pinyin_key_to_bib_file(input_bib, output_bib, using_common_strings):
    with open(input_bib, encoding="utf-8") as input_file:
        bibtex_str = input_file.read()
    parser = BibTexParser(common_strings=using_common_strings, ignore_nonstandard_types=False)
    bib_database = bibtexparser.loads(bibtex_str, parser)

    writer = bibtexparser.bwriter.BibTexWriter()
    with open(output_bib, encoding="utf-8", mode="w") as output_file:
        output_file.write(writer.write(add_pinyin_key_to_bib_database(bib_database)))
