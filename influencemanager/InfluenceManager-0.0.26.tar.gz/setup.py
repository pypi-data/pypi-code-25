"""
Backend module for retrieving top influencers from Twitter.
"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name="InfluenceManager",
    version="0.0.26",
    description="Backend module for retrieving top influencers from Twitter.",
    author="Ash Prince",
    author_email="i7629228@bournemouth.ac.uk",
    packages=find_packages(),
    include_package_data=True,
    scripts=["InfluenceManager/bin/topic_query"],
    install_requires=["pymongo", "nltk", "twython", "matplotlib", "wordcloud", "networkx"]
)
