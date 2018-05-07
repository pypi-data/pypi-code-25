from setuptools import setup

setup(name='uvsc',
      version='0.1',
      description='Python binding for uVision Socket interface',
      url='https://github.com/MatthiasHertel80/pyUVSC',
      author='Matthias Hertel - Arm',
      author_email='matthias.hertel@arm.com',
      license='Apache',
      packages=['uvsc'],
      install_requires=[
      ],
      classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],

      include_package_data=True,
      zip_safe=False)