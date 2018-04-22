from pprint import pprint

import click
from click import echo

from mindscli import get_api, requires_auth
from mindscli.output import Post


def _newsfeed(data, as_json, reverse=True):
    """Base fun for printing out data"""
    if as_json:
        pprint(data)
        return
    if reverse:
        data['activity'] = data['activity'][::-1]
    for post in data['activity']:
        if not post['blurb'] and not post['message']:
            continue
        post = Post.from_api_data(post)
        echo(str(post))


@click.group()
@click.option('-r', '--reverse', help='reverse order')
@click.pass_context
def newsfeed(ctx, reverse):
    """display newsfeed in the terminal"""
    ctx.obj['reverse'] = reverse


@newsfeed.command('boost')
@click.option('--json', 'as_json', help='return raw json data')
@click.pass_context
def newsfeed_boost(ctx, as_json):
    """boost section"""
    _newsfeed(get_api(ctx).newsfeed_boost(), as_json, not ctx.obj['reverse'])


@newsfeed.command('top')
@click.option('--json', 'as_json', help='return raw json data')
@click.pass_context
def newsfeed_top(ctx, as_json):
    """top section"""
    _newsfeed(get_api(ctx).newsfeed_top(), as_json, not ctx.obj['reverse'])


@newsfeed.command('subscribed')
@click.option('--json', 'as_json', help='return raw json data')
@click.pass_context
@requires_auth
def newsfeed_subscribed(ctx, as_json):
    """subscribed section"""
    _newsfeed(get_api(ctx).newsfeed_subscribed(), as_json, not ctx.obj['reverse'])


@newsfeed.command('channel')
@click.argument('guid_or_name_or_url')
@click.option('--json', 'as_json', help='return raw json data')
@click.pass_context
def newsfeed_channel(ctx, guid_or_name_or_url, as_json):
    """specific channel"""
    api = get_api(ctx)
    guid = api.get_guid(guid_or_name_or_url)
    _newsfeed(api.newsfeed_channel(guid), as_json, not ctx.obj['reverse'])
