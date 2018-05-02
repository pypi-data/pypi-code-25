from setuptools import setup, find_packages

setup(name='django-gdpr-ready',
        version='0.1',
        description='Django GDPR Compliance',
        url='https://github.com/GDPR-ready/django-gdpr-ready',
        author='Vikas Mishra',
        author_email='vikasmishra95@gmail.com',
        license='MIT',
        package_dir={'gdpr':'gdpr'},
        include_package_data=True,
        packages=find_packages(),
        zip_safe=False
        )
