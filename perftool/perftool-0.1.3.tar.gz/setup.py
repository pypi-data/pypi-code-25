from setuptools import setup

setup(name='perftool',
      version='0.1.3',
      description='The Performance Tool',
      url='https://github.com/Yajan/Perftool.git',
      author='Yajana',
      author_email='yajananrao@gmail.com',
      license='Apache License',
      packages=['perftool','perftool.executer','perftool.reporter'],
      zip_safe=False)