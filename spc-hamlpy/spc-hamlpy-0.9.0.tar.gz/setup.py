from setuptools import setup

# Note to Jesse - only push sdist to PyPi, bdist seems to always break pip installer
setup(name='spc-hamlpy',
      version='0.9.0',
      author='blacktear23',
      author_email='blacktear23@gmail.com',
      description='HAML like syntax for Django templates',
      keywords='haml django converter',
      url='http://github.com/jessemiller/HamlPy',
      download_url='http://github.com/jessemiller/HamlPy',
      packages=['hamlpy', 'hamlpy.template'],
      license='MIT',
      install_requires=[
      ],
      entry_points={
          'console_scripts': ['hamlpy = hamlpy.hamlpy:convert_files',
                              'hamlpy-watcher = hamlpy.hamlpy_watcher:watch_folder']
      }
    )
