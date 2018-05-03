from setuptools import setup

setup(name='perftool',
      version='0.1.6',
      description='The Performance Tool',
      long_description=open('README.md').read(),
      url='https://github.com/Yajan/Perftool.git',
      author='Yajana',
      author_email='yajananrao@gmail.com',
      license='Apache License',
      packages=['perftool','perftool.ext','perftool.reporter'],
      zip_safe=False)