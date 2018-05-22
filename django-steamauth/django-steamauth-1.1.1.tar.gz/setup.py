from setuptools import setup, find_packages

setup (
        name    =   'django-steamauth',
        packages = ['steamauth'],
        version     = '1.1.1',
        author  = 'blurfx',
        author_email    = 'pipsit@gmail.com',
        license          = 'MIT License',
        url         = 'https://github.com/blurfx/django-steamauth',
        description = 'steam login library for django',
        keywords=['django', 'steam', 'valve', 'steamid', 'openid'],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 2',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Framework :: Django',
            'Framework :: Django :: 1.10',
            'Framework :: Django :: 2.0',
            'License :: OSI Approved :: MIT License'
        ],
)