# -*- coding: utf-8 -*-

"""Console script for giaola_xml_utils."""

import click

from .parsers import XMLParser

@click.command()
def main(args=None):
    """Console script for giaola_xml_utils."""
    click.echo("Replace this message by putting your code into "
               "giaola_xml_utils.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")


@click.command()
@click.option('-element', 'element', required=True, help='High level element to return.')
@click.option('-path', 'path', required=True, help='Path to search. Can give more than one (,) separated.')
@click.option('-value', 'value', required=True, help='Value to search.')
@click.option('-file', 'file_path', required=True, help='File to search')
def find(element, path, value, file_path):
    import json
    parser = XMLParser(file_path, element)
    path = [token.strip() for token in path.split(',')]
    for element_dict in parser:
        for token in path:
            if element_dict.get(token) == value:
                click.echo(json.dumps(element_dict))
                continue


if __name__ == "__main__":
    main()
