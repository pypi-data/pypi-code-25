#!/usr/bin/env python
# created by BBruceyuan on 18-4-27

import argparse
from bugfreepy.CommentWrite import CommentWrite


def main():
    parser = argparse.ArgumentParser(description='write text pic to you python file')
    # nargs + represent match at most parameter
    parser.add_argument('file_path', nargs='+')
    parser.add_argument('--pic', default='default',
                        help='the pic you choose, it can be default, monster, god, jesus or buddist')
    args = parser.parse_args()

    file_paths = args.file_path
    pic = args.pic
    c = CommentWrite(file_paths, pic)
    c.write_comment()
