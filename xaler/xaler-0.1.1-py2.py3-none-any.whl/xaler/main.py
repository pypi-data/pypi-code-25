import click

@click.command()
@click.option('--save', default="Cheerleader", help='Save the...')
@click.option('--world', prompt='Save the',
              help='Save the...')

def hello(save, world):
    """Simple program that greets NAME for a total of COUNT times."""
    click.echo('You have saved the %s in order to save %s!' % (save, world))


