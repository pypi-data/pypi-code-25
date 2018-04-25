from setuptools import setup

setup(
    name='fancypipes',
    version='0.1.1dev',
    description='Making scikit-learn pipelines even more useful',
    url='https://github.com/ieaves/better-pipelines',
    author='Ian Eaves',
    author_email='ian.k.eaves@gmail.com',
    packages=['fancypipes'],
    license='MIT',
    install_requires=[
          'sklearn', 'pandas', 'numpy', 'scipy',
    ],
    zip_safe=False,
    include_package_data=True,
)
