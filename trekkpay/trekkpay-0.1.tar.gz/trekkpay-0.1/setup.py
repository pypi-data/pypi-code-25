from setuptools import setup

setup(
    name='trekkpay',
    version='0.1',
    author='Gökmen Görgen',
    author_email='gkmngrgn@gmail.com',
    description="TrekkPay Python SDK",
    long_description="The TrekkPay Python SDK is including an API client library.",
    url='https://github.com/gkmngrgn/trekkpay-python-sdk',
    install_requires=["requests>=0.11.1,<3.0"],
    license='MIT',
    py_modules=['trekkpay'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
