from setuptools import setup

setup(name='socialbladeclient',
      version='0.2',
      description='Social Blade Unofficial Client',
      url='http://github.com/meauxt/socialbladeclient',
      author='Mohamad Tarbin',
      author_email='mhed.t91@gmail.com',
      license='MIT',
      packages=['socialbladeclient'],
       install_requires=[
          'requests',
          'lxml'
      ],
      zip_safe=False)
