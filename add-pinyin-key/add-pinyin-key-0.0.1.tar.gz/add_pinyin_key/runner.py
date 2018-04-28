#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from add_pinyin_key import add_pinyin_key_to_bib_file


def main():
    parser = argparse.ArgumentParser(description='Add pinyin keys to chinese bib entries.')
    parser.add_argument('input_bib')
    parser.add_argument('output_bib')
    args = parser.parse_args()

    add_pinyin_key_to_bib_file(args.input_bib, args.output_bib)


if __name__ == "__main__":
    main()