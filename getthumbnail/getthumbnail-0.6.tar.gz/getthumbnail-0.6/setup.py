from setuptools import setup
from distutils.core import Extension

setup(name='getthumbnail',
      description="Uses libraw to pull thumbnails from raw images",
      author="Mark Murnane",
      author_email="mark@hackafe.net",
      url="https://github.com/bitbyt3r/getthumbnail",
      version='0.6',
      ext_modules=[
          Extension('getthumbnail',
                    sources=['getthumbnail.c'],
                    libraries=['raw']
                    )
          ]
     )
