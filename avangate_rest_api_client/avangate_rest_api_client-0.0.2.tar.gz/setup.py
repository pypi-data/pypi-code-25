from setuptools import setup

setup(
    name='avangate_rest_api_client',
    version='0.0.2',
    packages=['avangate_rest_api_client'],
    url='https://github.com/onursa/avangate_rest_api_client',
    license='MIT',
    author='Onur Salgit',
    author_email='mail@onur.org',
    description='Python Client for Avangate REST API',
    install_requires=["requests"]
)