# -*- coding: utf-8 -*-

import click
import sys

from minds import Minds, Profile
from mindscli.cli.profile import profile
from mindscli.cli.interact import upvote, downvote, delete
from mindscli.cli.newsfeed import newsfeed
from mindscli.cli.notifications import notifications
from mindscli.cli.show import show
from mindscli.cli.post import post
from mindscli.cli.user import user


@click.group()
@click.option('-u', 'username', help='username of minds channel')
@click.option('-p', 'password', help='password of minds channel')
@click.option('--proxy', 'proxy', help='proxy for minds requests')
@click.option('-s', 'save', help='save current profile locally', is_flag=True)
@click.option('-c', '--profile', 'profile', help='load local profile config')
@click.pass_context
def cli(ctx, username, password, profile, save, proxy):
    """Console interaction with minds"""
    if profile and (username or proxy or password):
        sys.exit(f'profile command cannot be used with config commands username, password or proxy')
    if bool(username) != bool(password):
        sys.exit(f'both username and password need to be provided')
    save = save if username or profile else False
    ctx.obj = {}
    if profile:
        try:
            ctx.obj['minds'] = Minds(Profile.from_config(profile))
        except FileNotFoundError:
            sys.exit(f'profile {profile} does not exist')
    else:
        ctx.obj['profile'] = Profile(username or '', password or '', proxy=proxy)


cli.add_command(newsfeed)
cli.add_command(notifications)
cli.add_command(post)
cli.add_command(upvote)
cli.add_command(downvote)
cli.add_command(profile)
cli.add_command(user)
cli.add_command(delete)
cli.add_command(show)

if __name__ == "__main__":
    cli()
