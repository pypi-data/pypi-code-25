import click
from mindscli import get_api
from mindscli.cli import print_response


@click.group()
@click.pass_context
def user(ctx):
    """Manage minds.com user"""
    pass


@user.command('register')
@click.argument('email')
@click.pass_context
@print_response(everything=True)
def user_register(ctx, email):
    """register an user"""
    return get_api(ctx, login=False).register(email)
