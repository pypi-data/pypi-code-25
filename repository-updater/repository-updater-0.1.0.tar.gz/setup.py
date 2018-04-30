"""
Hass.io add-ons repository updater setup
"""
from setuptools import setup

setup(
    name='repository-updater',
    version='0.1.0',
    url='https://github.com/hassio-addons/repository-updater',
    license='MIT',
    author='Franck Nijhof',
    author_email='frenck@addons.community',
    description='Hass.io add-ons repository updater',
    long_description='''
        Hass.io add-ons repository updater.

        Reads remote add-on repositories, determines versions and generates
        changelogs to update the add-on repository fully automated.

        Mainly used by the Community Hass.io add-ons project.

        Please note, this program cannot be used with the general documented
        Hass.io add-on repository approach.
    ''',
    platforms='any',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities'
    ],
    packages=['repositoryupdater'],
    install_requires=[
        'click==6.7',
        'crayons==0.1.2',
        'GitPython==2.1.9',
        'Jinja2==2.10',
        'PyGithub==1.39',
        'python-dateutil==2.7.2',
        'PyYAML==3.12',
        'semver==2.7.9',
    ],
    entry_points='''
        [console_scripts]
            repository-updater=repositoryupdater.cli:repository_updater
            repository-updater-git-askpass=repositoryupdater.cli:git_askpass
    '''
)
