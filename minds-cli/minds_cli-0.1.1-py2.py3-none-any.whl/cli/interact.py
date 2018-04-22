import click
from minds.utils import web_to_api

from mindscli import requires_auth
from mindscli import get_api
from mindscli.cli import print_response


@click.command('upvote')
@click.argument('guid_or_url')
@click.pass_context
@requires_auth
@print_response('status')
def upvote(ctx, guid_or_url):
    """
    upvote content
    """

    api = get_api(ctx)
    guid = api.get_guid(guid_or_url)
    return api.upvote(guid)


@click.command('downvote')
@click.argument('guid_or_url')
@click.pass_context
@requires_auth
@print_response('status')
def downvote(ctx, guid_or_url):
    """
    downvote content
    """
    api = get_api(ctx)
    guid = api.get_guid(guid_or_url)
    return api.downvote(guid)


@click.command('delete')
@click.argument('url')
@click.pass_context
@requires_auth
@print_response('message')
def delete(ctx, url):
    """
    delete content
    """
    api = get_api(ctx)
    url = web_to_api(url)
    return api.delete(url)
