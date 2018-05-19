from setuptools import setup


setup(
    name='stempl',
    description='HTML templates with just Python',
    url='http://www.github.com/gabrielhora/stempl',
    author='Gabriel Hora',
    author_email='gabriel@switchpayments.com',
    version='1.0.0',
    license='MIT',
    packages=['stempl'],
    include_package_data=True,
    zip_safe=False,
    tests_require=['tox>=3.0.0'],
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='html template'
)
