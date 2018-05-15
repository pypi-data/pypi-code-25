from setuptools import setup, find_packages


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='smartbetaapi',
    python_requires='>3.4',
    version='0.3',
    description='Client Library for calling SmartBeta system.',
    author='Enda McGarry',
    author_email='enda.mcgarry@amundi.com',
    platforms=['any'],  # or more specific, e.g. 'win32', 'cygwin', 'osx'
    license='Amundi ',
    url='https://tfs.intramundi.com/tfs/AmundiProjects/_git/SBA-SmartBeta_ScriptAPI',
    packages=find_packages(),
    install_requires=['marshmallow-enum>=1.4.1', 'marshmallow>=3.0.0b8', 'requests', 'pandas'])
    #include_packadge_data=True)
    #test_suite = 'smartbetaapi.tests.test_suite.run_test')
