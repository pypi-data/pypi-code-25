import click
import textwrap
import pytest

from packaging.requirements import Requirement

from spaken import helpers


@pytest.fixture
def requirements_file(tmpdir):
    path = tmpdir.join('requirements.txt')
    path.write(textwrap.dedent(
        r"""
        --trusted-host example.com
        -e git+https://github.com/jazzband/django-robots#egg=django-robots==3.1
        Django-healthchecks==1.4.0
        wsgi-basic-auth-healthchecks
        zeep \
        ==2.5.0
    """))
    return str(path)


def test_get_storage_backend_s3():
    helpers.get_storage_backend('s3://my-bucket/my-prefix')


def test_get_storage_backend_invalid():
    with pytest.raises(click.UsageError):
        helpers.get_storage_backend('file://my-bucket/my-prefix')


def test_read_requirements(requirements_file):
    requirements, pip_arguments = helpers.parse_requirements(requirements_file)
    assert requirements == [
        Requirement('Django-healthchecks==1.4.0'),
        Requirement('wsgi-basic-auth-healthchecks'),
        Requirement('zeep==2.5.0'),
    ]


def test_write_requirements(requirements_file):
    requirements, pip_arguments = helpers.parse_requirements(requirements_file)
    helpers.write_requirements(requirements, pip_arguments, requirements_file)

    requirements, pip_arguments = helpers.parse_requirements(requirements_file)

    with open(requirements_file, 'r') as fh:
        content = fh.read()
    assert '--trusted-host example.com' in content

    assert requirements == [
        Requirement('Django-healthchecks==1.4.0'),
        Requirement('wsgi-basic-auth-healthchecks'),
        Requirement('zeep==2.5.0'),
    ]

