#!/usr/bin/env python3
import argparse
import re
import sys
from glob import glob

desc = """Create passages from CoNLL-U files including complete tokenization"""


class ConlluPassageCreator:
    def create_passages(self, ids, filenames):
        passages = {}
        for pattern in filenames:
            filenames = glob(pattern)
            if not filenames:
                raise IOError("Not found: " + pattern)
            for filename in sorted(filenames):
                with open(filename, encoding="utf-8") as f:
                    external_id = None
                    tokens = []
                    try:
                        for line in f:
                            line = line.strip()
                            m = re.match("^# sent_id = (.*)", line)
                            if m:
                                external_id = m.group(1)
                            elif line:
                                tokens.append(line.split("\t")[1])
                            else:
                                passages[external_id] = tokens
                                external_id = None
                                tokens = []
                        if tokens:
                            passages[external_id] = tokens
                    except (IndexError, AssertionError) as e:
                        raise ValueError(filename) from e
        with open(ids) as f, open(ids + ".passages.txt", "w", encoding="utf-8") as fout:
            for external_id in f:
                print(" ".join(passages[external_id.strip()]), file=fout)
                print("##", file=fout)

    @staticmethod
    def add_arguments(argparser):
        argparser.add_argument("ids", help="external ids file")
        argparser.add_argument("filenames", nargs="+", help="filename pattern of CoNLL-U files")


def main(**kwargs):
    ConlluPassageCreator().create_passages(**kwargs)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description=desc)
    ConlluPassageCreator.add_arguments(argument_parser)
    main(**vars(argument_parser.parse_args()))
    sys.exit(0)

