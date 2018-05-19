import argparse
import os
import sys
import logging

import nbgrader_merge

FORMAT = '[%(levelname)s] %(filename)s/%(lineno)s %(message)s'


def exists(fname):
    if not os.path.exists(fname):
        msg = "`%s` not found" % fname
        raise argparse.ArgumentTypeError(msg)

    return fname


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('source', help='Exercise directory/file containing your answers', type=exists)
parser.add_argument('destination', help='Updated exercise directory/file', type=exists)
parser.add_argument('--debug', help='Debug mode', action='store_true')


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    args = parser.parse_args(args)

    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(format=FORMAT, level=level)

    if os.path.isdir(args.source) and os.path.isdir(args.destination):
        nbgrader_merge.merge_dirs(args.source, args.destination)
    elif os.path.isfile(args.source) and os.path.isfile(args.destination):
        nbgrader_merge.merge_files(args.source, args.destination, args.destination)
    else:
        raise RuntimeError("Both files must be either dirs or files")


if __name__ == "__main__":
    main()