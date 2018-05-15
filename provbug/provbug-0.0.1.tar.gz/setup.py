from setuptools import setup

setup(
    name="provbug",
    packages=["provbug"],
    version="0.0.1",    
    scripts=['provbug'],
    author=("Henrique Linhares, and Rômulo Ponciano"),
    author_email="hlinhares@id.uff.br",
    description="Supporting infrastructure to debug scientific experiments with prolog facts.",
    keywords=["scientific", "experiments", "provenance", "debug"],
    url="https://github.com/",
    python_requires='>=3.5',
    install_requires=["pyswip"],
    classifiers=[
    	'Development Status :: 3 - Alpha',

    	'License :: OSI Approved :: MIT License',

    	'Programming Language :: Python :: 3.5',
    	'Programming Language :: Python :: 3.6',
    ],
)