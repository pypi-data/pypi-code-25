import click



class Config(object):

    def __init__(self):
        self.verbose = False


pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('--verbose', is_flag=True)
@pass_config
def cli(config, verbose):
    config.verbose = verbose
    if config.verbose:
        click.echo('We are in verbose mode.')

@cli.command()
@click.option('-s','--string', default='World', help='This is the thing that is greeted.')
@click.option('-r','--repeat', default=1, help='How many types you wish to repeat the greetings?')
@click.argument('out', type=click.File('w'), default='-', required=False)
@pass_config
def say(config, string, repeat, out):
    """This function greets the user"""
    if config.verbose:
        click.echo('We are in say verbose mode')
    for x in range(repeat):
        click.echo('Hello {}!'.format(string), file=out)

