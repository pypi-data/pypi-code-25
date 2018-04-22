from pprint import pprint

import click

from mindscli import requires_auth, get_api
from mindscli.output import Notification


def _notification(data, as_json, reverse=True):
    if as_json:
        pprint(data)
        return
    if reverse:
        data['notifications'] = data['notifications'][::-1]
    for notification in data['notifications']:
        print(str(Notification.from_api_data(notification)))


@click.group()
@click.option('-r', '--reverse', help='reverse order')
@click.pass_context
def notifications(ctx, reverse):
    """display notifications in the terminal"""
    ctx.obj['reverse'] = reverse


@notifications.command('all')
@click.option('--json', 'as_json', help='return raw json data')
@click.pass_context
@requires_auth
def notifications_all(ctx, as_json):
    """show all notification categories"""
    _notification(get_api(ctx).notifications_all(), as_json, not ctx.obj['reverse'])


@notifications.command('tags')
@click.option('--json', 'as_json', help='return raw json data')
@click.pass_context
@requires_auth
def notifications_tags(ctx, as_json):
    """show only tag notifications"""
    _notification(get_api(ctx).notifications_tags(), as_json, not ctx.obj['reverse'])


@notifications.command('comments')
@click.option('--json', 'as_json', help='return raw json data')
@click.pass_context
@requires_auth
def notifications_comments(ctx, as_json):
    """show only comment notifications"""
    _notification(get_api(ctx).notifications_comments(), as_json, not ctx.obj['reverse'])


@notifications.command('groups')
@click.option('--json', 'as_json', help='return raw json data')
@click.pass_context
@requires_auth
def notifications_groups(ctx, as_json):
    """show only group notifications"""
    _notification(get_api(ctx).notifications_groups(), as_json, not ctx.obj['reverse'])


@notifications.command('subscriptions')
@click.option('--json', 'as_json', help='return raw json data')
@click.pass_context
@requires_auth
def notifications_subscriptions(ctx, as_json):
    """show only subscription notifications"""
    _notification(get_api(ctx).notifications_subscriptions(), as_json, not ctx.obj['reverse'])


@notifications.command('votes')
@click.option('--json', 'as_json', help='return raw json data')
@click.pass_context
@requires_auth
def notifications_votes(ctx, as_json):
    """show only vote notifications"""
    _notification(get_api(ctx).notifications_votes(), as_json, not ctx.obj['reverse'])
