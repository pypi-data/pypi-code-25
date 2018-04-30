from setuptools import setup

setup(name='rss2toot',
      version='0.0.2',
      description='Toot emitter from RSS feed using Mastodon.py',
      packages=['rss2toot'],
      install_requires=['requests', 'Mastodon.py', 'feedparser'],
      python_requires='>=3.5',
      url='https://gitlab.com/petzah/rss2toot',
      author='Peter Zahradnik',
      author_email='petzah+rss2toot@znik.sk',
      license='MIT',
      keywords='rss mastodon toot',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Communications',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
      ])
