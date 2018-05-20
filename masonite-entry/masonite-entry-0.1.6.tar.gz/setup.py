from setuptools import setup

setup(
    name="masonite-entry",
    version='0.1.6',
    packages=[
        'entry',
        'entry.api',
        'entry.api.models',
        'entry.commands',
        'entry.migrations',
        'entry.providers',
    ],
    install_requires=[],
    include_package_data=True,
)
