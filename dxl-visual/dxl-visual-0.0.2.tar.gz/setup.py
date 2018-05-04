from setuptools import setup, find_packages
setup(name='dxl-visual',
      version='0.0.2',
      description='Visualization library.',
      url='https://github.com/Hong-Xiang/dxvisual',
      author='Hong Xiang',
      author_email='hx.hongxiang@gmail.com',
      license='MIT',
      namespace_packages=['dxl'],
      packages=find_packages('src/python'),
      package_dir={'': 'src/python'},
      install_requires=[],
      zip_safe=False)
