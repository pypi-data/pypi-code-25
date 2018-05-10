from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='CRO Tax Debtors',
    version='0.5.0',

    description='List of Croatian tax debtors',
    long_description=readme(),
    long_description_content_type='text/markdown',

    url='https://github.com/arrrlo/CRO-Tax-Debtors',
    licence='MIT',

    author='Ivan Arar',
    author_email='ivan.arar@gmail.com',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='croatia, tax, debt',

    packages=['cro_tax_debtors'],
    install_requires=[
        'click~=6.7',
        'colorama~=0.3',
        'db-transfer~=0.5.0',
        'requests~=2.18.4',
        'lxml==4.2.1',
        'python-slugify~=1.2.5',
        'pyfiglet~=0.7.5',
        'termcolor~=1.1.0',
        'progress >= 1.2, < 1.3',
        'six~=1.11.0',
    ],
    entry_points={
        'console_scripts': [
            'crotaxdebtors=cro_tax_debtors.cli:cli'
        ],
    },

    project_urls={
        'Source': 'https://github.com/arrrlo/CRO-Tax-Debtors',
    },
)
