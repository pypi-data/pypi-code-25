from setuptools import setup


setup(
    name='lektor-yandex-metrica',
    version='0.1.2',
    author='Alex Khomchenko',
    author_email='akhomchenko@gmail.com',
    url='https://github.com/gagoman/lektor-yandex-metrica',
    license='MIT',
    description='Adds support for Yandex Metrica to Lektor CMS',
    keywords='Lektor plugin',
    long_description=open('README.rst').read(),
    py_modules=['lektor_yandex_metrica'],
    entry_points={
        'lektor.plugins': [
            'yandex-metrica = lektor_yandex_metrica:YandexMetricaPlugin',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Framework :: Lektor',
        'Environment :: Plugins'
    ]
)
