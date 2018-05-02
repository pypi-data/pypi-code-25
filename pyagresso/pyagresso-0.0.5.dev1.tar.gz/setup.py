from setuptools import setup, find_packages


# Don't import analytics-python module here, since deps may not be installed
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pymarketo'))

# python setup.py register -r pypi
# python setup.py sdist upload -r pypi

long_description = '''
This module helps developers work with the Agresso Unit4 (ver. Milestone 4) Query Engine
SOAP webservice easily without worry about the transport layer/protocol and getting data in easible
ingestible formats: JSON, CSV

Example:
    ```python
    from pyagresso.api import Agresso
    username = os.getenv('AGRESSO_USERNAME')
    password = os.getenv('AGRESSO_PASSWORD')
    client = os.getenv('AGRESSO_CLIENT')
    instance_url = os.getenv('AGRESSO_INSTANCE_URL')
    ag = Agresso(username, password,client,instance_url)
    about_response_as_xml = ag.about()
    ```

Todo:
    * Add methods to get response as JSON
    * Add methods to get response as CSV
    * Add internal helpers to parse xml (schema+records)
    * Make QueryEngine methods into submodule and add capability for extension into other Agresso modules
    * Version the SDK for various Agresso releases

Note: 
    * Not using bdd in this library due to small size of module undertest

'''

setup(
    name='pyagresso',
    version='0.0.5dev1',
    description='Python Client for Unit4 Agresso System',
    url='https://github.com/osamakhn/pyagresso',
    author='Osama Khan',
    author_email='osamakhn@gmail.com',
    license='MIT License',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'requests'
    ],
    long_description=long_description,
    keywords='Unit4 Agresso Milestone4',
    classifier=['Development Status :: 3 - Alpha',
                'Intended Audience :: Developers',
                'Programming Language :: Python :: 3'],
    project_urls={
        'Source': 'https://www.github.com/osamakhn/pyagresso'
    }
)
