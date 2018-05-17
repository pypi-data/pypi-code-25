import os
from setuptools import setup, find_packages

from dist_utils import fetch_requirements
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(BASE_DIR, 'requirements.txt')

install_reqs, dep_links = fetch_requirements(REQUIREMENTS_FILE)

setup(
    name='log_suraj',
    version=0.1,
    description='using logger to store logs in /var/log folder',
    author='Suraj',
    author_email='suraj.iot257@gmail.com',
    url='https://github.com/SURAJTHEGREAT/logger.git',
    license='Apache License (2.0)',
    download_url='https://github.com/SURAJTHEGREAT/logger.git',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_reqs,
    dependency_links=dep_links,
    test_suites='tests',
    zip_safe=False
)
