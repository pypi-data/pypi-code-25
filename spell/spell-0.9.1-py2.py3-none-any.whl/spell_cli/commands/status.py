# -*- coding: utf-8 -*-
import click

from api_client.user_client import UserClient
from spell_cli.exceptions import api_client_exception_handler
from spell_cli.utils import HiddenOption


@click.command(name="status",
               short_help="Show information on account billing")
@click.option("--raw", help="Display output in raw format.", is_flag=True, default=False, cls=HiddenOption)
@click.pass_context
def status(ctx, raw):
    client = UserClient(token=ctx.obj["config_handler"].config.token, **ctx.obj["client_args"])

    with api_client_exception_handler():
        billing_info = client.get_billing_info()

        click.echo("Current Plan: {}".format(billing_info.plan_name))
        if len(billing_info.period_machine_stats) > 0:
            click.echo("Usage since {} (will be invoiced around {}):".format(
                billing_info.last_machine_invoice_date,
                billing_info.next_machine_invoice_date
            ))
            for row in billing_info.period_machine_stats:
                click.echo("\t- {}: {} (${:,.2f})".format(row.machine_type_name, row.time_used, row.cost_used_usd))
        click.echo("Remaining free credit: ${:,.2f}".format(billing_info.remaining_credits_usd))
        if len(billing_info.total_machine_stats) > 0:
            click.echo("Total usage:")
            for row in billing_info.total_machine_stats:
                click.echo("\t- {}: {}".format(row.machine_type_name, row.time_used))
        click.echo("Run history:")
        click.echo("\t- total: {} runs".format(billing_info.total_runs))
        click.echo("\t- currently queued due to concurrency: {} runs".format(billing_info.concurrent_queued_runs))
        click.echo("\t- plan concurrency limit: {} runs".format(billing_info.concurrent_run_limit))
