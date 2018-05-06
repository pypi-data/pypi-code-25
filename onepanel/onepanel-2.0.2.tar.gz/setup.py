from setuptools import setup

setup(
    name="onepanel",
    version='2.0.2',
    packages = ['onepanel', 'onepanel.commands','onepanel.utilities'],
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    install_requires=[
        'requests',
        'click',
        'PTable',
        'configobj',
        'websocket-client',
        'humanize'
    ],
    entry_points='''
        [console_scripts]
        onepanel=onepanel.cli:main
    ''',
)
