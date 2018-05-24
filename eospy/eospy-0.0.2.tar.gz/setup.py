from setuptools import setup


setup(
    name='eospy',
    version='0.0.2',
    description='Python library of the EOS.IO project.',
    long_description='Python library of the EOS.IO project..',
    url='https://github.com/eostea/eospy',
    author='strahe',
    license='MIT',
    packages=['eospy'],
    install_requires=('requests', ),
    zip_safe=False,
    keywords=['eos', 'eosio', 'eospy', 'eospython'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
