
from setuptools import find_packages, Extension, Command
from distutils.core import setup


from Cython.Build import cythonize

from clustertree import __version__

extensions = []
extensions.append( Extension( "clustertree.src.clustertree",
                            [ "clustertree/src/clustertree.pyx",
                              "clustertree/src/cluster.c"], ) )

setup(version=__version__,
	  name='clustertree',
      description="Clustertrees.",
      long_description="Clustertrees.",
      install_requires=["cython", "numpy"],
      # Kanwei Li is the actual author, I just maintain it.
      author="Endre Bakken Stovner",
      author_email="endrebak85@gmail.com",
      # package_dir = { '': 'lib' },
      packages=find_packages(),
      setup_requires=['cython'],
      ext_modules=cythonize(extensions),
      package_data={'': ['*.pyx', '*.pxd', '*.h', '*.c']},
      include_dirs=["."],
)
