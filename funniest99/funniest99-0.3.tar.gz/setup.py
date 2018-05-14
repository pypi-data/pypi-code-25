from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='funniest99',
      version='0.3',
      description='The funniest joke in the world',
      long_description=readme(),
      url='https://github.com/liab25/funniest',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      scripts=['bin/funniest-joke'],
      packages=['funniest'],
      install_requires=['markdown'],
      zip_safe=False)
