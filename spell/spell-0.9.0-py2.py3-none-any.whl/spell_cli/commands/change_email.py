import click

from api_client.user_client import UserClient
from spell_cli.exceptions import (
    api_client_exception_handler
)


@click.command(name="change_email", short_help="Set a new email for your spell account")
@click.option("--new_email", "new_email",
              prompt="Enter your new spell email",
              help="Then email address you want to switch to")
@click.password_option(prompt="Enter your spell password",
                       help="your registered spell password",
                       confirmation_prompt=False)
@click.pass_context
def change_email(ctx, new_email, password, write=True):
    client = UserClient(token=ctx.obj["config_handler"].config.token, **ctx.obj["client_args"])
    with api_client_exception_handler():
        client.check_password(password)

    with api_client_exception_handler():
        client.change_email(new_email)

    click.echo("Email changed successfully!")
