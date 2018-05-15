from setuptools import setup, find_packages


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


reqs = parse_requirements('requirements.txt')


setup(name='markdown2jupyter',
    version='1.0',
    description='Markdown to Jupyter notebook converter',
    author='Jan Papousek',
    author_email='jan.papousek@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={
        'console_scripts': [
            'md2jupyter = markdown2jupyter.md2jupyter:cli'
        ]
    }
)
