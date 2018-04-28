#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from add_pinyin_key import add_pinyin_key_to_bib_file


def main():
    parser = argparse.ArgumentParser(description='Add pinyin keys to chinese bib entries.')
    parser.add_argument('input_bib')
    parser.add_argument('output_bib')

    parser.add_argument('--common-strings', dest='using_common_strings', action='store_true', help='If your bibtex contains months defined as strings such as month = jan, you will need this option.')
    # parser.add_argument('--no-common-strings', dest='using_common_strings', action='store_false', help='default')
    parser.set_defaults(feature=False)

    args = parser.parse_args()

    add_pinyin_key_to_bib_file(args.input_bib, args.output_bib, args.using_common_strings)


if __name__ == "__main__":
    main()