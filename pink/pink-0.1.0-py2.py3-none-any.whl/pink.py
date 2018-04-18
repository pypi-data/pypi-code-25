#!/usr/bin/env python
# coding=utf-8

import sys

import glob2
import black
import delegator

PEP8_LINE_LENGTH = 79


def command_line_runner():
    """
    主函数
    """
    python = sys.executable
    black_exec = black.__file__.rstrip('cdo')

    args = ' '.join(sys.argv[1:])
    for file in glob2.glob(args):
        c = delegator.run(
            f"{python} {black_exec} {file} --line-length {PEP8_LINE_LENGTH}"
        )
        print(c.out)
        print(c.err)
    sys.exit()


if __name__ == '__main__':
    command_line_runner()
