from distutils.core import setup
from spiral.version import VERSION


def do_setup():
    setup(
      name='tcollier-spiral',
      packages=['spiral'],
      version=VERSION,
      description='Iterate over a 2-D matrix in a spiral manner',
      author='Tom Collier',
      author_email='tcollier@gmail.com',
      url='https://github.com/tcollier/spiral',
      download_url=(
        'https://github.com/tcollier/spiral/archive/' + VERSION +
        '.tar.gz'),
      keywords=['spiral', 'matrix'],
      install_requires=[],
      classifiers=['Programming Language :: Python :: 3']
    )


if __name__ == '__main__':
    do_setup()
