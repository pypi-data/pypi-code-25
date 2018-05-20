import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs')
    codecs.register(func)

from setuptools import find_packages, setup

version = "0.1dev"

setup(
    name="grpc-django",
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django >= 1.9",
    ],
)