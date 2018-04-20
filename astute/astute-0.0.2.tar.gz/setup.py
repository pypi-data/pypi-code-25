from setuptools import setup


if __name__ == '__main__':
    setup(
        name="astute",
        version="0.0.2",
        description="Python AST utilities and experiments",
        author="Dmitri Pribysh",
        author_email="dmand@yandex.ru",
        url="https://github.com/dmand/astute",
        license='Apache 2.0',
        platform='any',

        long_description=open("README.md").read(),
        long_description_content_type='text/markdown',

        packages=["astute"],

        install_requires=[],  # nothing yet

        keywords=['ast', 'prettyprint', 'unparse'],
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: POSIX :: Linux",
            "Operating System :: MacOS",
            "Operating System :: Microsoft :: Windows",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
        ],
    )

