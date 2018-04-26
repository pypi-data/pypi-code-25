import click

from api_client.feedback_client import FeedbackClient
from spell_cli.exceptions import (
    api_client_exception_handler,
)
from spell_cli.log import logger


@click.command(name="feedback",
               short_help="Provide feedback to the Spell team")
@click.argument("message", nargs=-1)
@click.pass_context
def feedback(ctx, message):
    config = ctx.obj["config_handler"].config
    feedback_client = FeedbackClient(token=config.token, **ctx.obj["client_args"])

    if len(message) > 0:
        message = ' '.join(message)
    else:
        message = click.edit(text="Type your message here. " +
                                  "Save and exit to send, or just exit to abort.",
                             require_save=True)
    if not message:
        click.echo("Aborted.")
    else:
        click.echo("Posting feedback to the Spell team...")
        with api_client_exception_handler():
            logger.info("Sending feedback")
            feedback_client.post_feedback(message)
        click.echo("Post complete. Thanks so much for your feedback. We'll look into it right away!")
