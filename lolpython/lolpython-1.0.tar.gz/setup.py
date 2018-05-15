from setuptools import setup

setup(name='lolpython',
      version='1.0',
      description='lolcat port of the ruby version',
      url='https://github.com/Abhishek8394/lol-cat-py',
      author='Abhishek8394',
      author_email='apbytes@gmail.com',
      license='GPLv3',
      packages=['lol_py'],
      entry_points={
            'console_scripts': ['lolpython=lol_py.main:main']
      },
      include_package_date=True,
      zip_safe=False)