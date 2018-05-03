from distutils.core import setup
import cognite_prometheus

setup(
    # Application name:
    name="cognite-prometheus",

    # Version number (initial):
    version=cognite_prometheus.__version__,

    # Application author details:
    author="Matias Holte",
    author_email="matias.holte@cognite.com",

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/cognitedata/python-prometheus",

    packages=['cognite_prometheus'],

    description="Simple Prometheus wrapper.",

    # Dependent packages (distributions)
    install_requires=[
        "prometheus_client",
    ],
)