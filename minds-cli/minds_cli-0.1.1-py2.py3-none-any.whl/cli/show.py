import click
from click import echo

from mindscli import get_api
from mindscli.output import Post, Comment


def _print_comments(ctx, guid, limit=None):
    """
    :param ctx: click.context
    :param guid: guid of a post
    :param limit: amount of comments to retrieve
    """
    api = get_api(ctx)
    comments = api.comments(api.get_guid(guid), limit=limit)['comments']
    for comment in comments:
        echo(Comment.from_api_data(comment))


@click.group()
@click.pass_context
def show(ctx):
    """Create post/comment or display one"""
    pass


@show.command('comments')
@click.argument('guid')
@click.argument('count', default=3)
@click.pass_context
def show_comments(ctx, guid, count):
    """show comments"""
    _print_comments(ctx, guid, count)


@show.command('post')
@click.argument('guid')
@click.option('-c', '--comments', help='include comments', type=click.INT, default=0)
@click.pass_context
def show_post(ctx, guid, comments):
    """show single post"""
    api = get_api(ctx)
    echo(Post.from_api_data(api.newsfeed_single(guid)['activity']))
    if comments:
        _print_comments(ctx, guid, limit=comments)
