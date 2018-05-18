from setuptools import setup, find_packages

    
setup(

    name='supwsd',  # Required

    version='1.0.3',  # Required

    description='Python binding to the SupWSD RESTful service.',  # Required

    long_description="""# SupWSD\n\nSupWSD is a Python binding to an HTTP RESTful service that gives you programmatic access to SupWSD, a framework for supervised Word Sense Disambiguation (WSD).\n\nThe SupWSD service is available only for English and enforces a default limit of 100 free requests per 1 hour period.\n\n## Installation\n```\npip install supwsd\n```\n\n## Code Example\n```\nfrom supwsd.wsd import SupWSD\n\ntext="The human " + SupWSD.SENSE_TAG + "brain" + SupWSD.SENSE_TAG + " is quite proficient at word-sense disambiguation. The fact that natural language is formed "+ SupWSD.SENSE_TAG+"in a way"+ SupWSD.SENSE_TAG+" that requires so much of it is a " + SupWSD.SENSE_TAG + "reflection" + SupWSD.SENSE_TAG + " of that neurologic reality."\n\nfor sense in SupWSD().senses(text):\n    print("Word: {}\tLemma: {}\tPOS: {}\tSense: {}\tSource: {}\tCount: {}\tValid: {}\tMiss: {}".format(sense.word, sense.lemma, sense.pos,sense.key(),sense.source,sense.count(),sense.valid(),sense.miss()))\n\n    for result in sense.results:\n        print("Sense {}\tProbability: {}".format(result.key, result.prob))\n```\n\n## Links\n\n* <a target="_blank" href="https://supwsd-supwsdweb.1d35.starter-us-east-1.openshiftapps.com/supwsdweb/index.jsp">SupWSD Toolkit</a>\n* <a target="_blank" href="https://supwsd-supwsdweb.1d35.starter-us-east-1.openshiftapps.com/supwsdweb/api-python.jsp">SupWSD API Guide</a>\n* <a target="_blank" href="https://supwsd-supwsdweb.1d35.starter-us-east-1.openshiftapps.com/supwsdweb/demo.jsp">SupWSD Demo</a>\n""",
    
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