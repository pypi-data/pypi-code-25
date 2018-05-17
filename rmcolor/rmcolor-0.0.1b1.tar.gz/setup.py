from setuptools import setup


def get_readme():
    readme = ''
    try:
        import pypandoc
        readme = pypandoc.convert('README.md', 'rst')
    except (ImportError, IOError):
        with open('README.md', 'r') as file_data:
            readme = file_data.read()
    return readme

setup(
	name = 'rmcolor',
	version = '0.0.1b1',
	author = 'Raudin Moreno',
	author_email = 'raudin247@gmail.com',
	description = 'Imprime texto a color en la consola',
    # long_description_content_type = 'text/marckdown',
	long_description = get_readme(),
	license = open('LICENSE').read(),	

    classifiers = [
    	'Development Status :: 4 - Beta',
    	'Intended Audience :: Developers',
    	'Intended Audience :: Information Technology',
    	'Programming Language :: Python :: 3.2',
    	'Programming Language :: Python :: 3.3',
    	'Programming Language :: Python :: 3.4',
    	'Programming Language :: Python :: 3.5',
    	'Topic :: Software Development :: Libraries :: Python Modules',
    	'License :: OSI Approved :: MIT License'
    ],
    keywords='colores terminal texto color',
    packages=['rcolor'],
    package_dir = {'rcolor':'rcolor'},
)

# ejecutar python3 setup.py sdist en este mismo directorio
# para subirlo luego: python3 setup.py register
# mandarlo a pypi twine upload dist/*