from setuptools import setup, find_packages

setup(
    name='random_flavorpack',
    version='1.0.2',
    packages=find_packages(),
    include_package_data=True,
    url='https://gitlab.com/serial-lab/random-flavorpack',
    license='GPLv3',
    author='SerialLab Corp',
    author_email='slab@serial-lab.com',
    description='Randomized Number Flavorpack Plugin for SerialBox',
    keywords=('seriallab, quartet, randomized, numbers, serialbox, '
             'level-4 quartet'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
