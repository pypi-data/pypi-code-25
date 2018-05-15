# -*- coding: utf-8 -*-
import os
import click

from datetime import datetime

from .base import Penv
from . import VERSION


abspath = os.path.abspath
startup_script_bash = """
export PENV_SESSION_ID="$(python -c 'import uuid; print(uuid.uuid4())')"
export PENV_LOCK_FILE="/tmp/.penv-lock-$PENV_SESSION_ID"

function cd () {
    if [ -f $PENV_LOCK_FILE ]
    then
        builtin cd "$@"
    else
        touch $PENV_LOCK_FILE
        builtin cd "$@" && eval "$(penv scan)"
        rm $PENV_LOCK_FILE
    fi
}

function penv-ify () {
    VIRTUAL_ENV_DIRECTORY_PATH=$1

    mkdir -p .penv/.plugins

    if [ -d "$VIRTUAL_ENV_DIRECTORY_PATH" ]; then
        VIRTUAL_ENV_DIRECTORY_NAME="`basename $VIRTUAL_ENV_DIRECTORY_PATH`"
        echo "$VIRTUAL_ENV_DIRECTORY_NAME" > .penv/default
        builtin cd .penv                                                     && \
            ln -s ../$VIRTUAL_ENV_DIRECTORY_PATH $VIRTUAL_ENV_DIRECTORY_NAME && \
            builtin cd ..
    else
        penv venv-new
    fi

    cd .
}
"""


def execute(args, script=None, env=None):
    # TODO: is cleanup needed before calling exec? (open files, ...)
    command = script or args[0]
    os.execvpe(command, args, env or os.environ)


@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, default=False,
              help=('Prints version'))
@click.option('--startup-script', is_flag=True, default=False,
              help=('Just prints the command to be evaluated by given shell '
                    '(so far only bash supported)'))
@click.pass_context
def cli(ctx, version, startup_script):
    if ctx.invoked_subcommand is None and version:
        return click.echo(VERSION)

    if ctx.invoked_subcommand is None and startup_script:
        return click.echo(startup_script_bash)

    if ctx.invoked_subcommand is None:
        return click.echo(ctx.command.get_help(ctx))

    # Maybe I'll make "place" customizable at some point
    ctx.obj = {
        'place': abspath('.'),
        'startup_script': startup_script,
    }


# $> penv scan
@cli.command('scan')
@click.pass_context
def cli_scan(ctx, env=Penv()):
    penv_exists, place, stream = env.lookup(ctx.obj['place'])
    return click.echo(stream)


# $> penv venv-new
@cli.command('venv-new')
@click.pass_context
def cli_venv_new(ctx, env=Penv()):
    penv_exists, place, stream = env.lookup(ctx.obj['place'])
    if not penv_exists:
        msg = 'Could not find .penv directory (starting from: %s)' % place
        return click.echo(msg)

    datestamp = datetime.now().strftime('%Y_%m_%d__%H%M%S')
    venv_name = 'venvs/venv_%s' % (datestamp, )
    default_pointer = os.path.join(place, '.penv', 'default')
    with open(default_pointer, 'w') as fd:
        fd.write(venv_name)
    venv_place = os.path.join(place, '.penv', venv_name)
    option = '--prompt="\(%s__%s\)"' % (datestamp, os.path.basename(place))
    return execute(['virtualenv', venv_place, option])
