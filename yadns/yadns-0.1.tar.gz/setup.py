from setuptools import setup

setup(name='yadns',
      version='0.1',
      description='Wrapper for Yandex Mail for Domain DNS REST API',
      classifiers=[
        'Programming Language :: Python :: 2.7',
      ],
      keywords='yandex dns client mail pdd rest api',
      url='https://github.com/Feliksas/yadns',
      author='Andrey Ignatov',
      author_email='feliksas@feliksaslion.ru',
      license='GPLv3',
      packages=['yadns'],
      scripts=['bin/yadns-client'],
      install_requires=[
          'requests',
      ],
      include_package_data=True,
      zip_safe=False)
