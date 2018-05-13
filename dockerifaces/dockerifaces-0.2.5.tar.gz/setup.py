from setuptools import setup
#from distutils.core import setup

setup(name='dockerifaces',
      version='0.2.5',
      description='Use this package to find the virtual network of container -> connected to which virtual host network',
      url='https://github.com/atam84/dockerinterfaces',
      author='Mohamed Amine TAMDY',
      author_email='amine.tamdy@gmail.com',
      license='MIT',
      packages=['dockerifaces'],
      keywords='docker network interface route tcp udp analyser development',
      install_requires=[
          'docker',
          'ifaceinfo'
      ],
      classifiers=[  # Optional
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',
            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            # Pick your license as you wish
            'License :: OSI Approved :: MIT License',
            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
      ],
)
