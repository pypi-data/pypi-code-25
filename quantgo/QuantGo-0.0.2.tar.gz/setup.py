#-*- coding:utf-8 -*-



from setuptools import setup, find_packages

setup(
    name='QuantGo',
    version='0.0.2',
    description=('A powerful toolbox provides for quant'),
    long_description=open('README.txt').read(),
    author='liaozechuan',
    author_email='cloud.light@msn.cn',
    maintainer='liaozechuan',
    maintainer_email='cloud.light@msn.cn',
    license=' Apache',
    packages=find_packages(),
    platforms=['all'],
    url="https://github.com/Randomwak/QuantGO",
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

    ]
)
