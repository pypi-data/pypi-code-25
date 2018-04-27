import click
from packaging.requirements import Requirement

from spaken.s3 import S3Storage


def get_storage_backend(uri):
    if uri.startswith('s3://'):
        return S3Storage(uri)
    else:
        raise click.UsageError(
            "Unsupported storage uri (only s3:// is for now)")


def parse_requirements(filename):
    packages = []
    options = []

    with open(filename, 'r') as fh:
        for line in _process_requirement_lines(fh):
            if line.startswith('-'):
                options.extend(line.split())
            else:
                packages.append(Requirement(line))

    return packages, options


def _process_requirement_lines(fh):
    prev_line = None

    for line in fh:
        line = line.strip()

        # Remove comments
        if '#' in line:
            line = line[:line.index('#')].strip()

        # Skip empty lines
        if not line:
            continue

        if prev_line:
            line = prev_line + line

        if line.endswith('\\'):
            prev_line = line.rstrip('\\')
        else:
            prev_line = None
            yield line
