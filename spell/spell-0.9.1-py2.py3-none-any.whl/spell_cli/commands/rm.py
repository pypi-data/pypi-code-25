import sys

import click

from api_client.runs_client import RunsClient
from spell_cli.exceptions import api_client_exception_handler, ExitException
from spell_cli.log import logger


@click.command(name="rm",
               short_help="Remove a finished or failed run")
@click.argument("run_ids", required=True, nargs=-1)
@click.pass_context
def rm(ctx, run_ids):
    token = ctx.obj["config_handler"].config.token
    r_client = RunsClient(token=token, **ctx.obj["client_args"])

    logger.info("Deleting run ids={}".format(run_ids))
    exit_code = 0
    for run_id in run_ids:
        try:
            with api_client_exception_handler():
                r_client.remove_run(run_id)
        except ExitException as e:
            exit_code = 1
            e.show()
    sys.exit(exit_code)
