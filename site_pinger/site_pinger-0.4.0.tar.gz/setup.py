from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '0.4.0'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='site_pinger',
    version=__version__,
    description='python program for check work in site urls',
    long_description=long_description,
    url='https://github.com/assigdev/site_pinger',
    download_url='https://github.com/assigdev/site_pinger/tarball/' + __version__,
    license='BSD',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
      'Environment :: Console',
      'Environment :: Web Environment',
      'Operating System :: POSIX :: Linux',
      'Topic :: System :: Monitoring',
      'Topic :: Utilities',
      'Topic :: Internet :: WWW/HTTP',
    ],
    keywords='util, test site, ping',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    test_suite='tests',
    author='Arsen Khalilov',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='assigdev@gmail.com',
    entry_points={
              'console_scripts': [
                  'site_pinger = site_pinger.__main__:main',
                  'site_pinger_conf = site_pinger.utils:get_conf'
              ]
          },
)
