from setuptools import setup, find_packages

from vmware.extract import __version__

setup(
    name='vmware-extract',
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'python-dateutil','pandas==0.20.3','pandas==0.20.3','requests==2.10.0','pika==0.11.0','mock==2.0.0','path.py',
    ],
    entry_points = {
              'console_scripts': [
                  'cam_private=vmware.extract.command_process:main',
              ],
          },
)
