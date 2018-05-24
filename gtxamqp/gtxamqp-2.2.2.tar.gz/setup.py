import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

requirements = parse_requirements('requirements.txt')
test_requirements = parse_requirements('requirements-test.txt')

dependencyLinks = []
for idx, r in enumerate(requirements):
	if r.startswith("http") or r.startswith("git+http"):
		dependencyLinks.append(r)
		requirements[idx] = r.split("#egg=")[1].replace('-', '==')

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import shlex
        import pytest
        errcode = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errcode)


setup(
    name='gtxamqp',
    version='2.2.2',
    url='http://github.com/devsenexx/gtxamqp',
    license='MIT License',
    author='Oded Lazar',
    tests_require=test_requirements,
    install_requires=requirements,
    dependency_links=dependencyLinks,
    cmdclass={'test': PyTest},
    author_email='odedlaz@gmail.com',
    description='AMQP Reconnecting Client for Twisted',
    packages=find_packages(),
    include_package_data=True,
    platforms='linux',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    extras_require={
        'testing': ['pytest'],
    }
)
