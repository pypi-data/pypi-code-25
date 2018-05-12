from setuptools import setup

setup(name='cryptocompy2',
      packages=['cryptocompy2'],
      version='0.1.1.1',
      description='Simple wrapper for the public Cryptocompare API.',
      keywords = '',
      author='Danny Chua',
      author_email='dannychua@somewhere.somewhere',
      url='https://github.com/dannychua/cryptocompare2',
      download_url='https://github.com/dannychua/cryptocompy2/archive/0.1.1.1.tar.gz',
      license='MIT',
      python_requires='>=3',
      install_requires=['requests'],)