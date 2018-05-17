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
	name = 'rmcolors',
	version = '0.0.1b0',
	author = 'Raudin Moreno',
	author_email = 'raudin247@gmail.com',
	description = 'Imprime texto a color en la consola',
    # long_description_content_type = 'text/marckdown',
	long_description = get_readme(),
	license = open('LICENSE').read(),	
	url='https://github.com/raudin17/rmcolors',
    
    keywords='colores terminal texto color',
    packages=['rmcolors'],
    package_dir = {'rmcolors':'rmcolors'},
)

# ejecutar python3 setup.py sdist en este mismo directorio
# para subirlo luego: python3 setup.py register
# mandarlo a pypi twine upload dist/*