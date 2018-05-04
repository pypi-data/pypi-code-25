from setuptools import setup, find_packages

class About(object):
    NAME='sequence_tagging'
    VERSION='0.1.5'
    AUTHOR='blester125'
    EMAIL=f'{AUTHOR}@gmail.com'
    URL=f'https://github.com/{AUTHOR}/{NAME}'
    DL_URL=f'{URL}/archive/{VERSION}.tar.gz'
    LICENSE='MIT'

setup(
    name=About.NAME,
    version=About.VERSION,
    description="Sequence Tagging powered by the Averaged Perceptron.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author=About.AUTHOR,
    author_email=About.EMAIL,
    url=About.URL,
    download_url=About.DL_URL,
    license=About.LICENSE,
    packages=find_packages(),
    package_data={
        'sequence_tagging': [
            'sequence_tagging/data/pos_model.p',
            'sequence_tagging/data/pos_tagdict.p',
            'sequence_tagging/data/chunk_model.p',
            'sequence_tagging/data/chunk_tagdict.p',
            'sequence_tagging/data/atis_model.p',
            'sequence_tagging/data/atis_tagdict.p',
        ],
    },
    include_package_data=True,
    install_requires=[
    ],
    keywords=["NLP", "sequence tagging", "ML"],
    ext_modules=[],
)
