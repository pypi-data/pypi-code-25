from setuptools import setup, find_packages

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='context_explorer',
    url='https://gitlab.com/stemcellbioengineering/context-explorer',
    author='Joel Ostblom', author_email='joel.ostblom@gmail.com',
    # Needed to actually package something
    packages=find_packages(),  # ['context_explorer'],
    # scripts=['bin/tile_wells'],
    entry_points={
        'console_scripts': ['context_explorer=context_explorer:main']},
    # Needed for dependencies
    install_requires=[
        'matplotlib', 'joblib', 'scikit-learn', 'joblib', 'numpy',
        'pandas', 'shapely', 'matplotlib', 'natsort', 'seaborn', 'scipy',
        'pyqt5', 'scikit-image'],
    # Python version
    python_requires='>=3.6',
    # include_setup_data=True,
    # Package data
    package_data={
        'context_explorer': [
            'sample-data/ce-sample.csv',
            'icons/ce-icon-keep-white.ico',
            'icons/ce-icon-keep-white.png']},
    # *strongly* suggested for sharing
    version='1.1.0',
    # The license can be anything you like
    license='BSD-3',
    description='''A tool that facilitates analyses of data extracted from
        microscope images of cells''',
    # We will also need a readme eventually (there will be a warning)
    long_description=open('README.md').read()
)
