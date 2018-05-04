from setuptools import setup, find_packages

class About(object):
    NAME='word_tokenizer'
    VERSION='0.0.1'
    AUTHOR='blester125'
    EMAIL=f'{AUTHOR}@gmail.com'
    URL=f'https://github.com/{AUTHOR}/{NAME}'
    DL_URL=f'{URL}/archive/{VERSION}.tar.gz'
    LICENSE='MIT'

setup(
    name=About.NAME,
    version=About.VERSION,
    description='',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author=About.AUTHOR,
    author_email=About.EMAIL,
    url=About.URL,
    download_url=About.DL_URL,
    license=About.LICENSE,
    packages=find_packages(),
    package_data={
        'word_tokenizer': [
        ],
    },
    include_package_data=True,
    install_requires=[
    ],
    keywords=[],
)
