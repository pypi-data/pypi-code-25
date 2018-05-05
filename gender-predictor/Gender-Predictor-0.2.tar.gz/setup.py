from setuptools import setup

setup(
    name='Gender-Predictor',  # This is the name of your PyPI-package.
    version='0.2',  # Update the version number for new releases
    scripts=['gender_predictor/GenderClassifier.py']  # The name of your script, and also the command you'll be using for calling it
)
