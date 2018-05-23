from distutils.core import setup
from dappmx.info import LIB_VERSION

setup(
  name='dappmx',
  packages=['dappmx'],
  version=LIB_VERSION,
  description='Dapp payments',
  author='Dapp payments',
  author_email='contacto@dapp.mx',
  url='https://github.com/DappPayments/Dapp-SDK-Python',
  download_url='https://github.com/DappPayments/Dapp-SDK-Python/archive/0.7.tar.gz',
  keywords=['dapp', 'dapp payments', 'dappmx'],
  classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Developers',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'License :: OSI Approved :: MIT License',
  ],
  install_requires=[
      'requests',
      'pycryptodomex',
  ],
  license='MIT License',
  include_package_data=True,
  zip_safe=True,
)
