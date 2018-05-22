from ftpbackup import __VERSION__
from setuptools import setup, find_packages

REQUIREMENTS = [
    'pathspec',
]

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='ftpbackup',
    version= __VERSION__,
    description = 'Backup the folder to FTP!',
    long_description = readme(),
    author = 'mickey9910326',
    author_email = 'mickey9910326@gmail.com',
    url='https://github.com/mickey9910326/ftpbackup',
    license = 'MIT',
    packages=find_packages(),
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'ftpbk = ftpbackup.__main__:run',
        ],
    },
    install_requires=REQUIREMENTS
)
