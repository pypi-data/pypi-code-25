from setuptools import setup, find_packages

setup(
    name="maple_guard",
    version='0.2.1',
    zip_safe=False,
    platforms='any',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=['maple', 'redis', 'gevent'],
    scripts=['maple_guard/bin/run_maple_guard.py'],
    url="https://github.com/dantezhu/maple_guard",
    license="BSD",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="maple guard",
)
