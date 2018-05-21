from distutils.core import setup

setup(
    name='pigg',
    version='0.1.2',
    description='a machine learning api frame',
    author='zcfrank1st',
    author_email='zhchaos@gmail.com',
    url='https://github.com/zcfrank1st/piggy',
    packages=['pigg'],

    requires=(
       'tornado (==4.5.3)',
    ),
)