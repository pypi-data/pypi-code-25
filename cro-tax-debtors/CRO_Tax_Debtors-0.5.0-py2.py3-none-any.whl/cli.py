import yaml
import click

import cro_tax_debtors
from cro_tax_debtors.screen import Screen
from cro_tax_debtors.debtors import Debtors, CategoryDone


@click.group()
@click.pass_context
@click.option('-f', '--file_path', type=click.File(mode='r'), help='Input YAML file')
def cli(ctx, file_path):
    ctx.obj = {'data': yaml.load(file_path.read())['website']['porezna-uprava']}


@cli.command()
@click.pass_context
@click.option('-p', '--print_in_terminal', default=False, is_flag=True, help='Print in terminal')
def parse(ctx, print_in_terminal):

    screen = Screen()

    for category in ctx.obj['data']:

        if not category['enabled']:
            continue

        for page in range(1, 2000):
            try:
                spider = getattr(cro_tax_debtors.spiders, category['spider'])(category['url'].format(page))
                save_handler = getattr(cro_tax_debtors.save_handlers, category['save_handler'])(category)
                Debtors(spider, save_handler, screen, category).parse(print_in_terminal)

            except CategoryDone:
                break


@cli.command()
@click.pass_context
@click.option('-n', '--name', help='Name of the debtor')
def find(ctx, name):

    screen = Screen()

    for category in ctx.obj['data']:

        if not category['enabled']:
            continue

        save_handler = getattr(cro_tax_debtors.save_handlers, category['save_handler'])(category)
        Debtors(save_handler=save_handler, screen=screen, category_data=category).find(name)


@cli.command()
@click.pass_context
def delete(ctx):

    for category in ctx.obj['data']:

        if not category['enabled']:
            continue

        save_handler = getattr(cro_tax_debtors.save_handlers, category['save_handler'])(category)
        res = Debtors(save_handler=save_handler, category_data=category).delete()

    click.echo()
