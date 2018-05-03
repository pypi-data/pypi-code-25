import argparse
from .. import followup_advocate


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version', action='version', version=followup_advocate.__version__)
    subparsers = parser.add_subparsers(help='sub-command help')

    authors = argparse.ArgumentParser(add_help=False)
    authors.add_argument(
        'authors', metavar="'A. Einstein (IAS)'", nargs='*', help='Authors')

    def add_command(func, **kwargs):
        subparser = subparsers.add_parser(
            func.__name__, **dict(kwargs, help=func.__doc__))
        subparser.set_defaults(func=func)
        return subparser

    cmd = add_command(followup_advocate.authors, parents=[authors])

    cmd = add_command(followup_advocate.compose, parents=[authors])
    cmd.add_argument(
        '-m', '--mailto', action='store_true',
        help='Open new message in default e-mail client [default: false]')
    cmd.add_argument('gracedb_id', metavar='G123456', help='GraceDB ID')

    cmd = add_command(followup_advocate.compare_skymaps)
    cmd.add_argument(
        'paths', nargs='+', metavar='G123456/filename.fits.gz',
        help='Specify sky maps by GraceDB ID and filename')

    args = parser.parse_args(args)
    args.func(args)
