#!/usr/bin/env python
import os
import shutil
import tempfile
import time

import click
from pip._internal import main as pip_command

from spaken import __version__
from spaken.finder import collect_filenames
from spaken.helpers import (
    get_storage_backend, parse_requirements, write_requirements)


class Command:

    def run(self, bucket_uri, destination, requirements):
        start_time = time.time()

        packages, pip_arguments = parse_requirements(requirements)
        self._pip_arguments = pip_arguments

        self._destination = destination
        self._work_path = tempfile.mkdtemp()
        self._storage = get_storage_backend(bucket_uri)

        with tempfile.TemporaryDirectory() as tmp_path:
            self._temp_path = tmp_path

            missing_packages = self.download_wheel_files(packages)
            if missing_packages:
                self.download_sources(missing_packages)
                self.upload_wheel_files()

        duration = time.time() - start_time
        click.secho("\nAll done (%.2f seconds)  🚀\n" % duration, fg='green')

    def download_wheel_files(self, requirements):
        """Download pre-compiled packages from the wheel repository"""
        click.secho("Downloading pre-build wheel files", fg='green')

        filenames = self._storage.list_files()
        items, missing = collect_filenames(filenames, requirements)

        for item in items:
            target = os.path.join(self._destination, os.path.basename(item))
            if os.path.exists(target):
                click.echo(" - %s (already exists, skipping)" % item)
            else:
                click.echo(" - %s" % item)
                self._storage.get(item, target)
        return missing

    def download_sources(self, packages):
        """Download source packages from the pypi server and generate wheel
        files.

        """
        if not packages:
            return

        click.secho("Generating %d new wheel files" % len(packages), fg='green')

        tmp_reqfile = os.path.join(self._temp_path, 'requirements.txt')
        write_requirements(packages, self._pip_arguments, tmp_reqfile)

        pip_command([
            'wheel',
            '--requirement', tmp_reqfile,
            '--no-binary', ':all:',
            '--wheel-dir', self._temp_path
        ])

    def upload_wheel_files(self):
        """Upload all wheel files in the given path to the given bucket uri"""

        filenames = [
            fn for fn in os.listdir(self._temp_path) if fn.endswith('.whl')
        ]

        if not filenames:
            return

        click.secho("Uploading %d new wheel files" % len(filenames), fg='green')

        for filename in filenames:
            click.echo(' - %s' % filename)

            local_path = os.path.join(self._temp_path, filename)
            self._storage.upload(local_path, filename)

            shutil.move(
                local_path, os.path.join(self._destination, filename))


@click.command()
@click.option('--bucket-uri', required=True)
@click.option('--dest', default='wheelhouse')
@click.option('--requirement', '-r', required=True)
@click.version_option(version=__version__)
def main(bucket_uri, dest, requirement):
    cmd = Command()
    cmd.run(bucket_uri, dest, requirement)


if __name__ == '__main__':
    main()
