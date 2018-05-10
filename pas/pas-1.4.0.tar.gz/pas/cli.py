# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 bindh3x <os@bindh3x.io>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import click
from pas.manager import Pas

@click.group()
def cli():
    """Secure password manager."""
    pass

@click.command()
@click.option('--no-clipboard', '-n',
              help="do not copy key to clipboard.",
              default=False,
              is_flag=True)
@click.option('--key', '-k',
              help="get key value.",
              type=str,
              default=None)
@click.argument('account', required=True)
def read(*args, **kwargs):
    """Read account keys."""
    pas = Pas(options=kwargs)
    pas.read()

@click.command()
@click.option('--key', '-k',
              help="add a single key to an account.",
              type=str,
              default=None)
@click.argument('account', required=True)
def add(*args, **kwargs):
    """Add account."""
    pas = Pas(options=kwargs)
    pas.add()

@click.command()
@click.option('--key', '-k',
              help="specify key to remove.",
              type=str,
              default=None)
@click.argument('account', required=True)
def delete(*args, **kwargs):
    """Delete account or keys."""
    pas = Pas(options=kwargs)
    pas.delete()

@click.command()
@click.argument('query', required=True)
def search(*args, **kwargs):
    """Search."""
    pas = Pas(options=kwargs)
    pas.search()

@click.command()
def stats():
    """Get safe statistics."""
    pas = Pas(options=None)
    pas.stats()

cli.add_command(read)
cli.add_command(add)
cli.add_command(delete)
cli.add_command(search)
cli.add_command(stats)
