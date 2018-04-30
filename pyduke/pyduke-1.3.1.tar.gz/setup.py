from setuptools import setup, find_packages

setup(
    name='pyduke',
    version='1.3.1',
    description='Duke python utilities',
    url='http://github.com/cafeduke/pyduke',
    author='Raghunandan Seshadri',
    author_email='raghubs81@gmail.com',
    license='None',
    packages=find_packages(where='src'),
    package_dir={'':'src'},
    install_requires=[
        'scikit-learn', 'numpy', 'pandas', 
        'matplotlib',
        'pyfunctional', 
        ],
    zip_safe=False)


