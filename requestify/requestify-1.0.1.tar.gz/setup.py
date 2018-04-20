from setuptools import setup, find_packages

setup(name='requestify',
      version='1.0.1',
      description='convert curl to python requests code',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      author='Yue Minatsuki',
      author_email='yue.official.jp@gmail.com',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3.6',
      ],
      python_requires='>=3.6',
      url='https://github.com/minatsuki-yui/requestify',
      license="MIT Licence",
      packages=find_packages(),
      install_requires=["requests"]
      )
