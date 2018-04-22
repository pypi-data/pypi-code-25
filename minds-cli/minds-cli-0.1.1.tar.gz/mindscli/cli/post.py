import tempfile
import os
from functools import partial, wraps
from subprocess import call

import click
import sys
from click import echo

from markdown import markdown
from minds.endpoints import NEWSFEED_URLF
from minds.utils import api_to_web

from mindscli.cli import print_response
from mindscli import requires_auth, get_api
from mindscli.utils import multiline_input


def _text_from_editor(editor_cmd):
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.flush()
        call([editor_cmd, tf.name])  # will block here
        return tf.read().decode('utf8')


def _text_from_file(file):
    return file.read()


def confirmation_wrapper(func):
    def new_func():
        result = func()
        echo(result)
        while True:
            echo('send this msg? (y/n): ', nl=False)
            confirm = input()
            if 'y' in confirm:
                return result
            if 'n' in confirm:
                return ''

    return new_func


def constraint_wrapper(func):
    @wraps(func)
    def new_func():
        result = func()
        if not result.strip():
            echo('error: not sending empty message', err=True)
            sys.exit(1)
        return result

    return new_func


@click.group()
@click.pass_context
@click.option('-c', '--confirm', help='confirm the message before posting', is_flag=True)
@click.option('-e', '--editor', help='editor command to use for msg input', default=os.environ.get('EDITOR'))
@click.option('-f', '--file', help='take input from file', type=click.File())
@click.option('-s', '--stdin', help='take input from stdin', is_flag=True)
@click.option('--mature', help='mark content as mature/nsfw', is_flag=True)
def post(ctx, editor, stdin, file, mature, confirm):
    """Create post/comment or display one"""
    ctx.obj['mature'] = mature
    if stdin:
        msg_input_func = multiline_input
    elif file:
        msg_input_func = partial(_text_from_file, file)
    elif editor:
        msg_input_func = partial(_text_from_editor, editor)
    else:
        echo('No valid input found: either -e, -f or -stdin options must be used if $EDITOR env variable is not set')
        sys.exit(1)
    msg_input_func = constraint_wrapper(msg_input_func)
    ctx.obj['msg_input'] = confirmation_wrapper(msg_input_func) if confirm else msg_input_func


@post.command('newsfeed')
@click.argument('message', required=False)
@click.pass_context
@requires_auth
@print_response(('guid', NEWSFEED_URLF, api_to_web))
def post_newsfeed(ctx, message):
    """post a post under current user's newsfeed"""
    api = get_api(ctx)
    if not message:
        message = ctx.obj['msg_input']()
    return api.post_newsfeed(message=message, mature=ctx.obj['mature'])


@post.command('comment')
@click.argument('guid_or_url')
@click.argument('message', required=False)
@click.pass_context
@requires_auth
def post_comment(ctx, guid_or_url, message):
    """post a comment under a piece of content"""
    if not message:
        message = '\n'.join(multiline_input())
    api = get_api(ctx)
    guid = api.get_guid(guid_or_url)
    return api.post_comment(guid, message=message, mature=ctx.obj['mature'])


@post.command('blog')
@click.argument('title')
@click.argument('message', required=False)
@click.option('--draft', help='save as draft without publishing', is_flag=True)
@click.option('--license', help='blog license')
@click.option('--slug', help='url slug for the blog')
@click.option('--category', help='blog category')
@click.option('--', 'license', help='License for the blog')
@click.option('-m', '--markdown', 'from_markdown', help='write in markdown then convert to html', is_flag=True)
@print_response(('route', 'https://minds.com/{}'.format))
@click.pass_context
def post_blog(ctx, title, message, from_markdown, draft, license, slug, category):
    """post a blog under current user's blogfeed"""
    if not message:
        message = ctx.obj['msg_input']()
    if from_markdown:
        message = markdown(message)
    api = get_api(ctx)
    return api.post_blog(title=title, body=message, mature=ctx.obj['mature'], published=not draft,
                         license=license, slug=slug, category=category)
