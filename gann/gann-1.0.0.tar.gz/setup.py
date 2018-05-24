from setuptools import setup

setup(name='gann',
      version='1.0.0',
      description='Using genetic algorithms or combining gradient descent method to optimize neural network parameters',
      author='winycg',
      author_email='yangchuanguang@ict.ac.cn',
      url='https://blog.csdn.net/winycg/',
      license='MIT',
      keywords='Genetic Algorithm;Neural Network',
      project_urls={
            'Documentation': 'https://blog.csdn.net/winycg/',
            'Source': 'https://github.com/winycg/gann',
      },
      packages=['gann'],
      install_requires=['numpy>=1.14', 'tensorflow>=1.7'],
      python_requires='>=3'
     )