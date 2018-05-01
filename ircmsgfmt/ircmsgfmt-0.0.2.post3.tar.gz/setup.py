from setuptools import setup, find_packages
setup(
        name="ircmsgfmt",
        version="0.0.2-3",
        packages=find_packages(),
        install_requires=[],

        package_data={
            '':['*.md']
        },

        author="OriginCode",
        author_email="origincoder@yahoo.com",
        description="A formatter for IRC network log",
        license="GPLv3",
        keywords="IRC format formatter"
)
