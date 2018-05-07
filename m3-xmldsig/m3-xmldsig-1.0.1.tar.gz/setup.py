#coding: utf-8
from setuptools import setup, find_packages


setup(name='m3-xmldsig',
      version='1.0.1',
      url='https://bitbucket.org/barsgroup/xmldsig',
      license='MIT',
      author='BARS Group',
      author_email='kirov@bars-open.ru',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      description=u'Sign and verify RSA-SHA1 XML Digital Signatures',
      install_requires=(
          'lxml>=3.0',
          'rsa>=3.1.1',
          'six>=1.10.0',
      ),
      include_package_data=True,
      classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
      ],
      )
