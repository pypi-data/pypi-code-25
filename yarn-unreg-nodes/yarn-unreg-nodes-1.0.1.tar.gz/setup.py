from setuptools import setup

setup(
    name='yarn-unreg-nodes',
    version='1.0.1',
    description='List EC2 asg nodes that failed to reg with YARN cluster',
    url='http://github.com/seeker815/hadoop-yarn-unreg-nodes',
    author='Sai Kothapalle',
    author_email='ephemeral927@gmail.com',
    license='MIT',
    packages=['yarn_unreg_nodes'],
    zip_safe=False,
    scripts=['bin/yarn_unreg_nodes'],
    install_requires=[
        'boto',
        'requests',
        'argparse',
    ],
)
