__author__ = 'Ari-Pekka Honkanen'
__license__ = 'MIT'
__date__ = '17/11/2017'

from setuptools import setup

# memorandum (for pypi)
# python setup.py sdist upload


setup(name='bayesfit-ap',
      version='0.1.1',
      description="AP's Bayesian fitting and data analysis toolbox.",
      author='Ari-Pekka Honkanen',
      author_email='honkanen.ap@gmail.com',
      url='https://github.com/aripekka/bayesfit/',
      packages=[
                'bayesfit',
               ],
      install_requires=[
                        'numpy',
                        'scipy',
                        'matplotlib'
                       ],
      include_package_data=True,
)
