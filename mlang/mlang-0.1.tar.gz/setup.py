from setuptools import setup

setup(
    name='mlang',
    version='0.1',
    packages=['mlang', 'mlang.res', 'mlang_client', 'mlang_server', 'mlang_server.service'],
    url='',
    license='MIT',
    author='lishouguang',
    author_email='lishouguang@meizu.com',
    description='mlang client',
    long_description=open('README.md').read(),
    setup_requires=['progressbar2', 'requests-toolbelt']
)
