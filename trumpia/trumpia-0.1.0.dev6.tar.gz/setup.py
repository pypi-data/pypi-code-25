from distutils.core import setup

setup(name='trumpia',
      packages=['trumpia'],
      version='0.1.0.dev6',
      description='Python wrapper for Trumpia API',
      long_description=open('./README.md').read(),
      long_description_content_type='text/markdown',
      license='MIT',
      author='Alex Luis Arias',
      author_email='alex@alexarias.io',
      url='http://github.com/aleksarias/trumpia-python',
      keywords=['trumpia', 'api', 'python'],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
      ],
      install_requires=[
          'requests',
          'future'
      ],
      zip_safe=False, requires=['requests', 'future'])
