from setuptools import setup, find_packages

setup(
    name='SteemAX',
    version='0.1.dev0',
    packages=['steemax'],
    license='MIT',
    long_description=open('README.md').read(),
    keywords='steemit steem upvote exchange',
    url='http://github.com/artolabs/steemax',
    author='ArtoLabs',
    author_email='artopium@gmail.com',
    install_requires=[
        'python-dateutil',
        'steem',
        'pymysql',
    ],
    py_modules=['steemax'],
    entry_points = {
        'console_scripts': [
            'steemax=steemax.steemax:run',
        ],
    },
    python_requires='>=3.0',
    include_package_data=True,
    zip_safe=False
)

# sudo apt install python3 python3-pip libssl-dev python3-dev
# pip install --upgrade setuptools pip --user pip
