from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='mathtraq',
      version='1.0',
      description=('Create random arithmetic mp3 and/or jason files'),
      long_description=read('README.md'),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
         'Topic :: Multimedia :: Sound/Audio',
      ],
      keywords='MP3 mental math mathemagic arithmetic practice mathematics',
      url='https://github.com/mudbile/MathTraq',
      author='Daniel Dowsett',
      author_email='eulerspill@protonmail.com',
      license='MIT',
      packages=['mathtraq'],
      py_modules=['mathtraq'],
      include_package_data=True,
      install_requires=[
          'mpmath',
      ],
      zip_safe=False)