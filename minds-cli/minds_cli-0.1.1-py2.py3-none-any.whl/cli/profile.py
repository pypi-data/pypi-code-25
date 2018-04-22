import click
import os

from mindscli import requires_auth, get_api
from minds.profile import CONFIG_DIR


@click.group()
@click.pass_context
def profile(ctx):
    """Manage local user profiles"""
    pass


@profile.command('save')
@click.pass_context
@requires_auth
def profile_save(ctx):
    """save profile locally from provided credentials"""
    api = get_api(ctx)


@profile.command('list')
def profile_list():
    """list local profiles"""
    for p in os.listdir(CONFIG_DIR):
        print(p)
