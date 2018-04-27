from setuptools import setup, find_packages
import io


setup(
     name = "MLFeatureSelection",
     version = "0.0.1.9.1",
     keywords = ("pypi easy_install pip"),
     description = "geenral select features based on selected algorithm",
     long_description = open("README.rst", encoding='utf-8').read(),
     license = "MIT Licence",

     url = "https://github.com/duxuhao/Feature-Selection",
     author = "Xuhao(Peter) Du",
     author_email = "duxuhao88@gmail.com",

     packages = find_packages(),
     platforms = "Linux",
     classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
      ],

     install_requires = ["requires"]
     )
