from . import markdown2jupyter, create_executor
import click
import logging
import subprocess
import os.path


@click.command()
@click.argument('markdown_file')
@click.option('--output', '-o', default=None)
@click.option('--execution-path', default=None)
@click.option('--execution-timeout', default=600)
@click.option('--html', is_flag=True)
@click.option('--slides', is_flag=True)
def cli(markdown_file, output, execution_path, execution_timeout, html, slides):
    FORMAT = "%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d: %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    if output is None:
        output = '.'.join(markdown_file.split('.')[:-1]) + '.ipynb'
    if execution_path is not None:
        logging.info('Using exucutor on path "{}", with timeout {}'.format(execution_path, execution_timeout))
        executor = create_executor(execution_path, execution_timeout)
    else:
        executor = None
    logging.info('Writing jupyter notebook to {}'.format(output))
    markdown2jupyter(markdown_file, output, preprocessor=executor)
    if html:
        subprocess.call("jupyter nbconvert --to html {}".format(output).split())
    if html:
        subprocess.call("jupyter nbconvert --to slides {}".format(output).split())


if __name__ == '__main__':
    cli()
