from setuptools import setup

setup(name='prayer-times',
      version='1',
      description='Prayer times using aladhan.com API',
      url='http://github.com/meauxt/prayer-times',
      author='Mohamad Tarbin',
      author_email='mhed.t91@gmail.com',
      license='MIT',
      packages=['prayer-times'],
       install_requires=[
          'requests',
          'json'
      ],
      zip_safe=False)
