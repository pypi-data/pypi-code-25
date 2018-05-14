from setuptools import setup, find_packages

setup(
    name='Emulator',
    version='1.1',
    description='Python-Flask application to emulate IoT devices',
    author='Ashraya Shiva',
    author_email='ashraya@futurehome.no',
    packages=['Emulator'],
    include_package_data=True,
    package_data = {
        '': ['Emulator/static/prop_files/*.json'],
    },
    install_requires=[
        'flask',
    ],
)
