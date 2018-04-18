from setuptools import setup, find_packages
setup(name='dxl-fs',
      version='0.1.5',
      description='File system library.',
      url='https://github.com/Hong-Xiang/dxl',
      author='Hong Xiang',
      author_email='hx.hongxiang@gmail.com',
      license='MIT',
      namespace_packages=['dxl'],
      packages=find_packages('src/python'), 
      package_dir = {'': 'src/python'},
      install_requires=[
          'click',
          'rx',
          'fs',
      ],
      scripts=['src/cli/dxfs.py'],
    #   namespace_packages = ['dxl'],
      zip_safe=False)
