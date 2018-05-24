from setuptools import setup, find_packages

setup(
  name='morpheus-game-framework',
  version='0.8.5',
  description='Framework for developing games for the Morpheus platform',
  author='morpheus team',
  author_email='mihael@morpheuszone.com',
  license='MIT',
  install_requires=['pyyaml'],
  packages=find_packages(),
  classifiers=(
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ),
)
