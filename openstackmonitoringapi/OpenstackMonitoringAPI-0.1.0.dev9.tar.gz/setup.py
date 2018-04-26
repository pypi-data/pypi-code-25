from distutils.core import setup
import setuptools

setup(
    name='OpenstackMonitoringAPI',
    version='0.1.0.dev9',
    description="Thrift API for the de.NBI Openstack monitoring project",
    author='Marius Dieckmann',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3.6',
    ],
    packages=['OpenstackCloudMonitoringAPI'],
    install_requires=['thrift'],
)
