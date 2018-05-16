#!/usr/bin/env python3

import argparse
import sys
from glob import glob

from tqdm import tqdm

from ucca import layer0
from ucca.ioutil import read_files_and_dirs

desc = """Prints statistics on UCCA passages
"""


def main(args):
    for pattern in args.filenames:
        t = tqdm(read_files_and_dirs(glob(pattern)), file=sys.stdout, unit=" passages")
        for passage in t:
            t.set_postfix(id=passage.ID, size=len(passage.layer(layer0.LAYER_ID).all))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=desc)
    argparser.add_argument("filenames", nargs="+", help="files to process")
    main(argparser.parse_args())
