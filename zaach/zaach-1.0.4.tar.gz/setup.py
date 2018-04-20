from distutils.core import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='zaach',
    version='1.0.4',
    packages=['zaach',],
    author="Fabian Topfstedt",
    url="https://bitbucket.org/fabian/zaach",
    license='The MIT Licence',
    package_data={'': ['LICENCE', 'README.md']},
    long_description=readme(),
    keywords = ['base64url', 'timezone', 'conversion'],
    classifiers = [],
)
