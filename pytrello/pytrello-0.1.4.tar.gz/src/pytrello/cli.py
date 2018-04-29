"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mpytrello` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``pytrello.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``pytrello.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
import json
import os
import pytrello
import pytrello.api.card as card_api


# Create the top-level parser.
parser = argparse.ArgumentParser(description='Python wrapper for Trello API.')
subparsers = parser.add_subparsers(description='Commands', dest='subcommand')


# Adopted from https://mike.depalatis.net/blog/simplifying-argparse.html.
def argument(*name_or_flags, **kwargs):
    return ([*name_or_flags], kwargs)


def subcommand(args=[], parent=subparsers):
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator


@subcommand()
def configure(args):
    """Configure pytrello with Trello API key and token.
    """
    package_dir = os.path.dirname(pytrello.__path__[0])
    config_json = os.path.join(package_dir, 'pytrello', 'config.json')
    config_dict = dict()

    config_dict['key'] = input('Your Trello API key: ')
    config_dict['token'] = input('Your Trello API token: ')

    with open(config_json, 'w') as outFile:
        print(json.dumps(config_dict), file=outFile)


@subcommand([
    argument('-b', '--board', nargs='+', required=True),
    argument('-c', '--card', nargs='+', required=True),
    argument('-i', '--comment', nargs='+', default=None),
])
def comment(args):
    """Add comment to your trello card.
    """
    board_name = ' '.join(args.board)
    card_name = ' '.join(args.card)
    comment_ = ' '.join(args.comment) if args.comment is not None else None

    card_id = card_api.get_card_id(board_name, card_name)
    card_api.add_comment(card_id, comment_)


@subcommand([
    argument('-b', '--board', nargs='+', required=True),
    argument('-c', '--card', nargs='+', required=True),
    argument('-i', '--comment', nargs='+', default=None),
])
def done(args):
    """Mark your trello card as done.
    """
    board_name = ' '.join(args.board)
    card_name = ' '.join(args.card)
    comment_ = ' '.join(args.comment) if args.comment is not None else None

    card_id = card_api.get_card_id(board_name, card_name)
    card_api.mark_as_done(card_id, comment_)


def main(args=None):
    args = parser.parse_args(args=args)
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
