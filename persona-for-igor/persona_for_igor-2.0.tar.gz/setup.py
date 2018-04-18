from setuptools import setup, find_packages

setup(name='persona_for_igor',
      version='2.0',
      description='Persona_package_for_igor',
      long_description='For my owner Igor',
      classifiers=[
        'Programming Language :: Python :: 3.6',
      ],
      # keywords='persona hubs accounts',
      author='OlegStruk',
      author_email='struchok25@gmail.com',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False)