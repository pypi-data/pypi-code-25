from setuptools import setup

with open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()


setup(
    name='stempl',
    version='1.0.6',
    description='HTML templates with just Python',
    long_description=readme,
    url='http://www.github.com/gabrielhora/stempl',
    author='Gabriel Hora',
    author_email='gabriel@switchpayments.com',
    license='MIT',
    packages=['stempl'],
    include_package_data=True,
    zip_safe=False,
    tests_require=['tox==3.0.0'],
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='html template'
)
