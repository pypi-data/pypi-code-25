from setuptools import setup


setup(name='lichessbot',
      version='1.1.0',
      author='pythonflaskserverapps',
      author_email='pythonflaskserverapps@gmail.com',
      description='play on lichess with a bot',
      long_description='Play on lichess with a bot.',
      license='MIT',
      keywords="play lichess bot",
      url='https://github.com/pythonflaskserverapps/lichessbot',            
      packages=['lichessbot'],
      test_suite="test",
      python_requires=">=3.3",
      install_requires=[        
        "chardet==3.0.4",
        "future==0.16.0",
        "futures==3.1.1",
        "idna==2.6",
        "python-chess==0.23.5",
        "PyYAML==3.12",
        "requests==2.18.4",
        "urllib3==1.22",
        "backoff==1.5.0"
      ],
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
      ],
      entry_points={
        'console_scripts': ['lichessbot=lichessbot.lichessbot_main:startup'],
      },
      package_dir={
        'lichessbot': 'lichessbot'
      },
      include_package_data=False,
      zip_safe=False)

