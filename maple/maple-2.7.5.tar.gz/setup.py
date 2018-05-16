from setuptools import setup, find_packages
setup(
    name="maple",
    version="2.7.5",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=["events", "netkit", "protobuf >= 3.5.1", 'setproctitle'],
    scripts=[],
    url="https://github.com/dantezhu/maple",
    license="MIT",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="reliable, scalable, distributed server framework",
)
