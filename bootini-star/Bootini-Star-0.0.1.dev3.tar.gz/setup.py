"""Setup module for Bootini Star."""
__author__ = 'Ralph Seichter'

from setuptools import setup, find_packages

setup(
    name='Bootini-Star',
    version='0.0.1.dev3',
    description="Inspect EVE Online mail and skill queues in a web browser.",
    long_description=("Inspect EVE Online mail and skill queues in a web"
                      " browser. Inspired by CCP's discontinued EVE Gate"
                      " web application."),
    author='Ralph Seichter',
    author_email='bootini-star@seichter.de',
    url='https://github.com/rseichter/bootini-star.git',
    license='MIT',
    python_requires='>=3.4',
    packages=find_packages(exclude=['tests', 'tmp', 'venv']),
    data_files=[('Bootini-Star', ['LICENSE', 'wsgi.py']),
                ('Bootini-Star/db-static', ['db-static/db-helper.sh',
                                            'db-static/groups.sql.bz2', 'db-static/types.sql.bz2']),
                ],
    install_requires=[
        'Flask >= 0.12.2',
        'Flask-Login >= 0.4.1',
        'Flask-Migrate >= 2.1.1',
        'Flask-SQLAlchemy >= 2.3.2',
        'Flask-WTF >= 0.14.2',
        'passlib >= 1.7.1',
        'requests-oauthlib >= 0.8.0',
    ],
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
    ],
    project_urls={
        'Source': 'https://github.com/rseichter/bootini-star.git'
    },
)
