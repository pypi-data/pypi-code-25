import setuptools

setuptools.setup(name='iex-api-python',
                 version="0.0.2",
                 description='Fetch data from the IEX API',
                 long_description=open('README.md').read().strip(),
                 author='Daniel E. Cook',
                 author_email='danielecook@gmail.com',
                 url='http://www.github.com/danielecook/iex-api-python',
                 packages=['iex'],
                 keywords=['finance', 'stock', 'market', 'market-data', 'IEX', 'API'],
                 license='MIT License',
                 zip_safe=False)
