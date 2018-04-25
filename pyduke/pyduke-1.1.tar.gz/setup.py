from setuptools import setup, find_packages

setup(
    name='pyduke',
    version='1.1',
    description='Duke Python Utilities',
    long_description='General python utilities and machine learning utilities',
    url='http://github.com/cafeduke/pyduke',
    author='Raghunandan Seshadri',
    author_email='raghubs81@gmail.com',
    license='None',
    packages=find_packages(),
    install_requires=[
        'scikit-learn', 'numpy', 'pandas', 
        'matplotlib',
        'pyfunctional', 
        ],
    zip_safe=False)