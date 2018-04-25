from setuptools import setup

setup(
    name='pyduke',
    version='1.0',
    description='Duke python utilities',
    url='http://github.com/cafeduke/pyduke',
    author='Raghunandan Seshadri',
    author_email='raghubs81@gmail.com',
    license='None',
    packages=['pyduke'],
    install_requires=[
        'scikit-learn', 'numpy', 'pandas', 
        'matplotlib',
        'pyfunctional', 
        ],
    zip_safe=False)