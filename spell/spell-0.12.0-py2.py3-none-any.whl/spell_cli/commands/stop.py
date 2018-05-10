import click

from api_client.runs_client import RunsClient
from spell_cli.exceptions import (
    api_client_exception_handler,
)
from spell_cli.log import logger


@click.command(name="stop",
               short_help="Stop a current run, save all files created or modified")
@click.argument("run_id")
@click.pass_context
def stop(ctx, run_id):
    token = ctx.obj["config_handler"].config.token
    run_client = RunsClient(token=token, **ctx.obj["client_args"])

    with api_client_exception_handler():
        logger.info("Stopping run {}".format(run_id))
        run_client.stop_run(run_id)

    click.echo("Stopping run {}. Use 'spell logs -f {}' to view logs while job saves".format(run_id, run_id))
