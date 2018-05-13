from distutils.core import setup

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3 :: Only',
]

setup(
      name='oec',
      version='0.1.0',
      description='API Wrapper for The Observatory for Economic Complexity',
      author='Yahia Ali',
      license='MIT',
      url='https://github.com/yahiaali/oec',
      classifiers=classifiers,
      install_requires=['requests'],
      python_requires='>=3',
)
