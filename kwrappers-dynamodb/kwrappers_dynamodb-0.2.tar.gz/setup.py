from setuptools import setup, find_packages


def get_install_requires():
    with open('requirements.txt', 'r') as f:
        return f.read().splitlines()


def get_version():
    with open('version.txt', 'r') as f:
        return f.readline().split()[0]  # Filter out other junk


# Completely unnessesary but testing bitbucket pipelines and observing PyPi files
def get_python_version(py_version):
    return "{}.{}".format(py_version.major, py_version.minor)


setup(
    name='kwrappers_dynamodb',
    version=get_version(),
    description='Kwrappers helpers for dynamodb.',
    long_description='Support tools for AWS DynamoDB.',
    url='https://bitbucket.org/tim_kablamo/kwrappers',
    author='Tim Elson',
    author_email='tim.elson@kablamo.com.au',
    license='MIT',
    entry_points={
        'console_scripts': [
            'dbp=kwrappers.dynamodb.cli_apps.dynamodb_batch_prepare:main',
            'dynamo-batch-prepare=kwrappers.dynamodb.cli_apps.dynamodb_batch_prepare:main',
        ],
    },
    packages=find_packages(),
    install_requires=get_install_requires(),
    zip_safe=False,
    data_files=[
        'version.txt',
        'requirements.txt',
    ],
)
