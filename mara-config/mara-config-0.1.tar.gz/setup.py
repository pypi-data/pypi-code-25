from setuptools import setup, find_packages

setup(
    name='mara-config',
    version='0.1',

    description="Mara app composing and configuration infrastructure.",


    extras_require={
        'test': ['pytest',
                 'flask>=0.12', 'mara_page' # config views
        ],
    },

    dependency_links=[
        'git+https://github.com/mara/mara-page.git@1.2.3#egg=mara-page-1.2.3',
    ],

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

)
