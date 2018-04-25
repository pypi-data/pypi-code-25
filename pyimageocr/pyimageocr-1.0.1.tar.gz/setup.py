# this is your project's setup.py script
#python setup.py sdist upload 

import os
from distutils.command.register import register as register_orig
from distutils.command.upload import upload as upload_orig

from setuptools import setup


class register(register_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')

class upload(upload_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')
setup(name='pyimageocr',
      version='1.0.1',
      description='Python machine learning ocr.',
      url='https://github.com/Krprashant94/pyimageocr',
      author='Prashant Kumar',
      author_email='kr.prashant94@gmail.com',
      license='MIT',
      packages=['pyimageocr'],
      zip_safe=False,
      cmdclass={
        'register': register,
        'upload': upload,
    })