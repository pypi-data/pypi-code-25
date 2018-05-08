import click

from api_client.runs_client import RunsClient
from spell_cli.exceptions import (
    api_client_exception_handler,
)
from spell_cli.log import logger


@click.command(name="kill",
               short_help="Kill a current run")
@click.argument("run_id")
@click.pass_context
def kill(ctx, run_id):
    token = ctx.obj["config_handler"].config.token
    run_client = RunsClient(token=token, **ctx.obj["client_args"])

    with api_client_exception_handler():
        logger.info("Killing run {}".format(run_id))
        run_client.kill_run(run_id)

    logger.info("Successfully killed run {}".format(run_id))
    click.echo(run_id)
