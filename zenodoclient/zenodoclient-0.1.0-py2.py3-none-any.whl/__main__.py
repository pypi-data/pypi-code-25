from __future__ import print_function
import traceback

import attr
import click
from tabulate import tabulate
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.contrib.completers import WordCompleter

from zenodoclient.api import Zenodo, API_URL
from zenodoclient.models import Deposition


def pretty_print(obj):
    items = [('id', obj.id)]
    if isinstance(obj, Deposition):
        for f in attr.fields(obj.metadata.__class__):
            v = getattr(obj.metadata, f.name)
            if v:
                items.append((f.name, v))
        items.append(('files', [f_.id for f_ in obj.files]))

    maxfield = max(len(k) for k, v in items)
    lines = []
    for k, v in items:
        if isinstance(v, list):
            lines.append(click.style('{0}:'.format(k), bold=True))
            for vv in v:
                lines.append('  {0}'.format(vv))
        else:
            lines.append(u'{0} {1}'.format(click.style((k + ':').ljust(maxfield), bold=True), v))
    return '\n'.join(lines)


class Context(object):
    api = None
    depositions = {}
    deposition_files = {}


@click.group()
@click.option('--api-url', default=API_URL)
@click.option('--access-token', envvar='ZENODO_ACCESS_TOKEN')
@click.pass_context
def cli(ctx, api_url, access_token):
    ctx.obj.api = Zenodo(api_url=api_url, access_token=access_token)


def _ls(ctx, q):
    table = []
    for dep in ctx.obj.api.iter(q=q):
        ctx.obj.depositions[str(dep.id)] = dep
        table.append([dep.id, dep.metadata.title, dep.metadata.doi])
    click.echo(tabulate(table, headers=['ID', 'Title', 'DOI']))


@cli.command()
@click.option('-q', default=None)
@click.pass_context
def ls(ctx, q):
    _ls(ctx, q)


def _update(ctx, dep):
    dep = ctx.obj.depositions.get(dep)
    if not dep:
        dep = ctx.obj.api.retrieve(dep)
    md = {}
    k = prompt(u'key: ', completer=WordCompleter([f.name for f in attr.fields(dep.metadata.__class__)]))
    while k:
        v = prompt(u'value: ', default=getattr(dep, k, ''))
        if v:
            md[k] = v
        k = prompt(u'key: ', completer=WordCompleter([f.name for f in attr.fields(dep.metadata.__class__)]))
    dep = ctx.obj.api.update(dep, **md)
    ctx.obj.depositions[str(dep.id)] = dep
    click.echo(pretty_print(dep))


def fuzzyfinder(infix, choices):  # pragma: no cover
    return [c for c in choices if infix in c]


@cli.command()
@click.pass_context
def curate(ctx):
    commands = {
        'quit': lambda: None,
        'ls': lambda args: _ls(ctx, args[0] if args else None),
        'update': lambda args: _update(ctx, args[0]),
        'show': lambda args: click.echo(pretty_print(ctx.obj.api.retrieve(args[0]))),
        'help': lambda: print("Available Commands: %s" % ", ".join(sorted(commands))),
    }

    class TheCompleter(Completer):
        def get_completions(self, document, complete_event):
            word_before_cursor = document.get_word_before_cursor(WORD=True)
            words = document.text_before_cursor.split()
            if words and words[0] in commands:
                for ds in fuzzyfinder(word_before_cursor, ctx.obj.depositions.keys()):
                    yield Completion(ds, start_position=-len(word_before_cursor))
            else:  # elif word_before_cursor:
                for c in fuzzyfinder(word_before_cursor, commands):
                    yield Completion(c, start_position=-len(word_before_cursor))

    user_input = []
    while not user_input or user_input[0] != 'quit':
        try:
            user_input = prompt(u'zenodo> ', completer=TheCompleter()).split()
        except EOFError:
            break

        if len(user_input) == 0:
            continue  # ignore empty commands
        if user_input[0] not in commands:
            click.echo(click.style('Invalid command!', fg='red'))
            continue

        try:
            commands[user_input[0]](user_input[1:])
        except Exception as e:
            traceback.print_exc()
            click.echo(click.style('{0}: {1}'.format(e.__class__.__name__, e), fg='red'))

    click.echo('see ya!')


def main():
    return cli(obj=Context())


if __name__ == '__main__':
    main()
