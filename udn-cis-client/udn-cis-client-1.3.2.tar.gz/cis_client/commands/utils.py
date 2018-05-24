from functools import wraps
import sys
import imp

import requests
import click

import cis_client
from cis_client import exception
from cis_client.lib.cis_north import version_client

# import progressbar2 here (not progressbar)
correct_progressbar_loaded = False
for path in sys.path:
    try:
        imp.load_module('progressbar2', *imp.find_module('progressbar', [path]))
        import progressbar2
        pb = progressbar2.ProgressBar(max_value=100)
        correct_progressbar_loaded = True
        break
    except (ImportError, TypeError) as e:
        pass
if correct_progressbar_loaded is False:
    print "Please reinstall application. progressbar2 is not installed"
    sys.exit(1)


CONTEXT_SETTINGS = dict(auto_envvar_prefix='CIS_CLIENT')


def add_auth_options(func):
    @click.option('--brand-id', type=click.STRING, help='Brand Id')
    @click.option('--account-id', type=click.STRING, help='Account Id')
    @click.option('--group-id', type=click.STRING, help='Group Id')
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def add_host_options(func):
    @click.option('--aaa-host', required=True, type=click.STRING, help='AAA hostname.')
    @click.option('--north-host', required=True, type=click.STRING, help='CIS North hostname.')
    @click.option('--south-host', type=click.STRING, help='CIS South hostname.')
    @click.option('--insecure', type=click.BOOL, default=False,
                  help='Allow insecure server connections when using SSL')
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def add_credentials_options(func):
    @click.option('--username', required=True, type=click.STRING, help='AAA username.')
    @click.option('--password', required=True, type=click.STRING, help='AAA password.')
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except requests.HTTPError as e:
            print "Error: {}, reason: {}".format(str(e), e.response.text)
            sys.exit(1)
        except (exception.OptionException, exception.UploadConflictException) as e:
            print "Error:", e.message
            sys.exit(1)
        except Exception as e:
            raise
    return wrapper


def get_source_file_list_from_kwargs(**kwargs):
    split_values = lambda comma_separated_values: map(str.strip, map(str, comma_separated_values.split(',')))
    if kwargs.get('source_file_list') is not None and kwargs.get('source_file') is not None:
        raise exception.OptionException("Please specify only one option --source-file-list or --source-file")
    paths = []
    if kwargs.get('source_file_list') is not None:
        with open(kwargs['source_file_list']) as f:
            file_content = f.read()
        paths = map(str.strip, file_content.strip().split('\n'))
    if kwargs.get('source_file') is not None:
        paths = split_values(kwargs['source_file'])

    return paths


def check_cis_version(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cis_version = version_client.get_cis_version(**kwargs)
        if isinstance(cis_version, basestring):
            if not cis_version.startswith(cis_client.SUPPORTED_CIS_VERSION):
                print "Backend CIS version {} is not supported by udn-cis-client. Please install a new version of udn-cis-client:\n"\
                      "pip install --upgrade udn-cis-client".format(cis_version)
                sys.exit(1)
        else:  # dict
            from cis_client import cli
            cli_version_tuple = cli.app_version.version.split('.')
            cli_version_major = str(cli_version_tuple[0])
            cli_version_minor = str(cli_version_tuple[1])
            cis_version_tuple = cis_version['cis-client'].split('.')
            cis_version_major = str(cis_version_tuple[0])
            cis_version_minor = str(cis_version_tuple[1])
            if cli_version_major != cis_version_major or cli_version_minor != cis_version_minor:
                print "Backend CIS version is not supported by udn-cis-client. Current version of udn-cis-client is {cli_version}.\n"\
                      "To connect to server please install a new version of udn-cis-client:\n"\
                      "pip install udn-cis-client=={cis_version_major}.{cis_version_minor}".format(
                    cli_version=cli.app_version,
                    cis_version_major=cis_version_major,
                    cis_version_minor=cis_version_minor)
                sys.exit(1)
        func(*args, **kwargs)
    return wrapper


class ProgressBar(progressbar2.ProgressBar):
    def __init__(self, *args, **kwargs):
        super(ProgressBar, self).__init__(*args, **kwargs)
        self.exception = None

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.exception = exc_type
        self.finish()

    def update(self, value=None, force=False, **kwargs):
        if self.exception:
            value = 0
        super(ProgressBar, self).update(value, force, **kwargs)
