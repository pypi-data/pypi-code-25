from setuptools import setup

long_description = "Python module to generate power network model for GIC calculations. See github.com/TerminusEst/Power_Network for a detailed description"

setup(name = 'power_network_model',
      version='0.8',
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



