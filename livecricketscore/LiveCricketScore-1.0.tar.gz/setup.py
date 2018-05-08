from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='LiveCricketScore',
    url='https://github.com/manavrawat10/LiveScoreNotification',
    author='Manvenddra Rawat',
    author_email='manvenddra.rawat@gmail.com',
    # Needed to actually package something
    packages=['liveCricketScore'],
    # Needed for dependencies
    install_requires=['bs4','requests','win10toast','lxml'],
    # *strongly* suggested for sharing
    version='1.0',
    # The license can be anything you like
    license='Manvenddra',
    description='It will give you a notification in windows 10 with the live cricket score',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)