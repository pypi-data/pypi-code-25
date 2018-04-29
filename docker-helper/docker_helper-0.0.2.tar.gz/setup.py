from distutils.core import setup

setup(
    name='docker_helper',
    packages=['docker_helper'],
    version='0.0.2',
    description='Convenience utilities for Python applications in Docker containers',
    long_description=open('README.md').read(),
    license='MIT',
    author='Viktor Adam',
    author_email='rycus86@gmail.com',
    url='https://github.com/rycus86/docker_helper',
    download_url='https://github.com/rycus86/docker_helper/archive/0.0.2.tar.gz',
    keywords=['docker', 'container', 'cgroup', 'secret', 'config'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
)
