from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name = 'power_network_model',
      version='0.7',
      description='Python module to generate power network model for GIC calculations.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      keywords='geomagnetic space weather GICs',
      url='https://github.com/TerminusEst/Power_Network',
      author='Sean Blake',
      author_email='blakese@tcd.ie',
      license='MIT',
      packages=['power_network_model'],
      include_package_data=True,
      zip_safe=False)



