#!/usr/bin/env python
import io
import os
import shutil
import signal
import sys
import tempfile

import click
from pip._internal import main as pip_command

import boto3


def parse_requirements(requirements_file):
    """Parse the requirements file"""
    packages = []
    options = []
    with open('requirements.txt', 'r') as fh:
        for line in fh:
            if '#' in line:
                line = line[:line.index('#')].strip()

            if line.startswith('--'):
                options.extend(line.split())

            if '==' in line:
                packages.append(line.strip())

    return packages, options


class Command:

    def run(self, bucket_uri, destination, packages, options):
        self._register_signals()
        self._exit = False
        self._bucket_uri = bucket_uri
        self._wheel_destination = destination
        self._pip_options = options
        self._work_path = tempfile.mkdtemp()

        missing_packages = self.download_wheel_files(packages)
        self.download_sources(missing_packages)
        self.upload_wheel_files()

        shutil.rmtree(self._work_path)

    def _register_signals(self):
        def signal_handler(signal, frame):
            self._exit = True
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

    def _check_for_exit(self):
        if self._exit:
            sys.exit(0)

    def download_wheel_files(self, packages):
        """Download pre-compiled packages from the wheel repository"""
        missing_packages = []

        print("=======================")
        print("Downloading wheel files")
        print("=======================\n")

        index_content = bucket_to_pypi_index(self._bucket_uri)
        index_filename = os.path.join(self._work_path, 'index.html')

        with open(index_filename, 'w') as fh:
            fh.write(index_content)

        arguments = [
            'download', '--no-index', '--dest', 'wheelhouse/',
            '--find-links', index_filename
        ]

        for package in packages:
            self._check_for_exit()
            retval = pip_command(arguments + [package])
            if retval != 0:
                missing_packages.append(package)

        return missing_packages

    def download_sources(self, packages):
        """Download source packages from the pypi server and generate wheel
        files.

        """
        if not packages:
            return

        print("\n========================")
        print("Downloading new packages")
        print("========================\n")

        arguments = [
            'wheel', '--no-binary', ':all:', '--wheel-dir',
            self._work_path
        ]
        arguments += self._pip_options
        for package in packages:
            self._check_for_exit()
            pip_command(arguments + [package])
        print("\n")

    def upload_wheel_files(self):
        """Upload all wheel files in the given path to the given bucket uri"""
        bucket_name, bucket_path = parse_bucket_uri(self._bucket_uri)

        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)

        for filename in os.listdir(self._work_path):
            if not filename.endswith('.whl'):
                continue
            local_path = os.path.join(self._work_path, filename)
            key = os.path.join(bucket_path, filename)

            with open(local_path, 'rb') as fh:
                bucket.put_object(Key=key, Body=fh.read())

            # Move file to the destination dir
            shutil.move(
                local_path, os.path.join(self._wheel_destination, filename))


def parse_bucket_uri(uri):
    if '/' in uri:
        bucket_name, bucket_path = uri.split('/', 1)
        if not bucket_path.endswith('/'):
            bucket_path += '/'
    else:
        bucket_name = uri
        bucket_path = ''

    return (bucket_name, bucket_path)


def bucket_to_pypi_index(bucket_uri):
    """Generate an html file with all the known wheel files so pip can use it
    as an index.

    """
    fh = io.StringIO()

    bucket_name, bucket_path = parse_bucket_uri(bucket_uri)

    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    bucket_obj = s3.Bucket(bucket_name)

    fh.write('<html><body>')

    if bucket_path:
        objects = bucket_obj.objects.filter(Prefix=bucket_path)
    else:
        objects = bucket_obj.objects.all()

    for name in objects:
        filename = name.key
        url = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': name.bucket_name, 'Key': name.key})
        fh.write('<a href="%s">%s</a>' % (url, filename))
    fh.write('</body></html>')

    return fh.getvalue()



@click.command()
@click.option('--bucket-uri', required=True)
@click.option('--dest', default='wheelhouse')
@click.option('--requirements', '-r', required=True)
def main(bucket_uri, dest, requirements):
    packages, options = parse_requirements(requirements)

    cmd = Command()
    cmd.run(bucket_uri, dest, packages, options)


if __name__ == '__main__':
    main()
