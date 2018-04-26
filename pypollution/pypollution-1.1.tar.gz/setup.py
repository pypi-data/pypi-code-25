# this is your project's setup.py script
#python setup.py sdist upload

import os
from distutils.command.register import register as register_orig
from distutils.command.upload import upload as upload_orig

from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

class register(register_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')

class upload(upload_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')
setup(name='pypollution',
      version='1.1',
      description='A python library for making graph in real time (Hardware based Library).',
      author='Prashant Kumar',
      author_email='kr.prashant94@gmail.com',
      url='https://github.com/Krprashant94/pypollution',
      license='MIT',
      long_description = read('README'),
      packages=['pypollution'],
      zip_safe=True,
      cmdclass={
        'register': register,
        'upload': upload,
    })