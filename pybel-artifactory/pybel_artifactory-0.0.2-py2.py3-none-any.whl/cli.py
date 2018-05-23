# -*- coding: utf-8 -*-

"""Command line interface for PyBEL Artifactory."""

import sys

import click
import hashlib
from getpass import getuser

from pybel.constants import NAMESPACE_DOMAIN_OTHER
from pybel.resources import parse_bel_resource, write_annotation, write_namespace
from . import get_bel_resource_hash, hash_names
from .history import get_annotation_history, get_namespace_history


@click.group()
@click.version_option()
def main():
    """PyBEL-Artifactory Command Line Interface."""


@main.group()
def namespace():
    """Namespace file utilities."""


@namespace.command()
@click.argument('name')
@click.argument('keyword')
@click.argument('domain')
@click.argument('citation')
@click.option('--author', default=getuser())
@click.option('--description')
@click.option('--species')
@click.option('--version')
@click.option('--contact')
@click.option('--licenses')
@click.option('--values', default=sys.stdin, help="A file containing the list of names")
@click.option('--functions')
@click.option('--output', type=click.File('w'), default=sys.stdout)
@click.option('--value-prefix', default='')
def write(name, keyword, domain, citation, author, description, species, version, contact, licenses, values,
          functions, output, value_prefix):
    """Build a namespace from items."""
    write_namespace(
        name, keyword, domain, author, citation, values,
        namespace_description=description,
        namespace_species=species,
        namespace_version=version,
        author_contact=contact,
        author_copyright=licenses,
        functions=functions,
        file=output,
        value_prefix=value_prefix
    )


def _hash_helper(file):
    resource = parse_bel_resource(file)

    result = hash_names(
        resource['Values'],
        hash_function=hashlib.md5
    )

    click.echo(result)


@namespace.command()
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
def semhash(file):
    """Semantic hash a namespace file."""
    _hash_helper(file)


@namespace.command()
@click.argument('namespace_module')
def history(namespace_module):
    """Hash all versions on Artifactory."""
    for path in get_namespace_history(namespace_module):
        h = get_bel_resource_hash(path.as_posix())
        click.echo('{}\t{}'.format(path, h))


@namespace.command()
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin, help="Path to input BEL Namespace file")
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout,
              help="Path to output converted BEL Annotation file")
def convert_to_annotation(file, output):
    """Convert a namespace file to an annotation file."""
    resource = parse_bel_resource(file)

    write_annotation(
        keyword=resource['Namespace']['Keyword'],
        values={k: '' for k in resource['Values']},
        citation_name=resource['Citation']['NameString'],
        description=resource['Namespace']['DescriptionString'],
        file=output
    )


@main.group()
def annotation():
    """Annotation file utilities"""


@annotation.command()
@click.argument('annotation_module')
def history(annotation_module):
    """Output the hashes for the annotation resources' versions."""
    for path in get_annotation_history(annotation_module):
        h = get_bel_resource_hash(path.as_posix())
        click.echo('{}\t{}'.format(path, h))


@annotation.command()
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
def semhash(file):
    """Semantic hash a BEL annotation."""
    _hash_helper(file)


@annotation.command()
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin, help="Path to input BEL Namespace file")
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout,
              help="Path to output converted BEL Namespace file")
@click.option('--keyword', help="Set custom keyword. useful if the annotion keyword is too long")
def convert_to_namespace(file, output, keyword):
    """Convert an annotation file to a namespace file."""
    resource = parse_bel_resource(file)
    write_namespace(
        namespace_keyword=(keyword or resource['AnnotationDefinition']['Keyword']),
        namespace_name=resource['AnnotationDefinition']['Keyword'],
        namespace_description=resource['AnnotationDefinition']['DescriptionString'],
        author_name='Charles Tapley Hoyt',
        namespace_domain=NAMESPACE_DOMAIN_OTHER,
        values=resource['Values'],
        citation_name=resource['Citation']['NameString'],
        file=output
    )


if __name__ == '__main__':
    main()
