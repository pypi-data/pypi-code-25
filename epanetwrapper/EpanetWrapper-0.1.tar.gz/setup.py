from setuptools import setup

setup(name='EpanetWrapper',
      packages=['ENWrapper'],
      version='0.1',
      description='A python wrapper used to ease simulations and analytics',
      url='https://github.com/cccristi07/EpanetWrapper',
      author='Cristian Cazan',
      author_email='cccristi07@gmail.com',
      license='MIT',
      # classifiers=[
      #   #'Development status :: Beta',
      #   "Intendend Audience :: Developers",
      #   "License :: MIT",
      #   "Operating System :: POSIX",
      #   "Operating System :: Windows",
      #   "Programming Language :: Python :: 3"
      #   ],
      zip_safe=False,
      install_requires=[
          "numpy",
          "matplotlib",
          "epanettools",
          'pandas',
          'plotly'
      ]

      )
