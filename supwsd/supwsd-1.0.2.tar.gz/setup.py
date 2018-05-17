from setuptools import setup, find_packages

    
setup(

    name='supwsd',  # Required

    version='1.0.2',  # Required

    description='Python binding to the SupWSD RESTful service.',  # Required

    long_description="""# SupWSD\n\nSupWSD is a Python binding to an HTTP RESTful service that gives you programmatic access to SupWSD, a framework for supervised Word Sense Disambiguation (WSD).\n\nThe SupWSD service is available only for English and enforces a default limit of 100 free requests per 1 hour period.""",
    
    long_description_content_type='text/markdown',

    url='https://supwsd-supwsdweb.1d35.starter-us-east-1.openshiftapps.com/supwsdweb/index.jsp',  

    author='Simone Papandrea',  # Optional

    author_email='papandrea.simone@gmail.com',  # Optional

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    license='CC BY-NC-SA 3.0',
    
    keywords='Supervised Word Sense Disambiguation',

    packages=find_packages(), 

)