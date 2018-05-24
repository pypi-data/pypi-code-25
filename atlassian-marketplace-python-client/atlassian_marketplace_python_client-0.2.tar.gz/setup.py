from distutils.core import setup

setup(
    name='atlassian_marketplace_python_client',
    version='0.2',
    description='The Python Client for the Atlassian Marketplace',
    author='Jean Petry',
    author_email='jpetry@seibert-media.net',
    packages=['atlassian_marketplace_api'],
    install_requires=[
        'requests==2.18.4',
    ],
)
