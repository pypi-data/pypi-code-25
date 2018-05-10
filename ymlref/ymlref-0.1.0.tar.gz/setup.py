"""ymlref: load Yaml documents with possibility to resolve references."""

from setuptools import setup, find_packages

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development']

with open('README.rst') as readme:
    LONG_DESCRIPTION = readme.read()

setup(
    name='ymlref',
    license='MIT',
    description=__doc__,
    use_scm_version=True,
    long_description=LONG_DESCRIPTION,
    platforms=["Linux", "Unix"],
    setup_requires=['setuptools_scm'],
    install_requires=['pyaml', 'jsonpointer', 'pytest-runner'],
    tests_require=['pytest', 'pytest-mock'],
    author='Konrad Jałowiecki <dexter2206@gmail.com>',
    author_email='dexter2206@gmail.com',
    packages=find_packages(exclude=['tests', 'tests.*', 'examples']),
    keywords='yml json jsonpointer'
)
