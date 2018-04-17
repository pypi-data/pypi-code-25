import setuptools

import pynucamino

setuptools.setup(

    name="pynucamino",
    version=pynucamino.__version__,
    author="Nathaniel Knight",
    author_email="nknight@cfenet.ubc.ca",
    description=(
        "Python bindings to nucamino, A nucleotide to amino acid alignment "
        "program optimized for virus gene sequences."
    ),
    license="MIT",
    url="https://github.com/hcv-shared/pynucamino",

    test_suite="test",

    python_requires=">=3.6,<4.0",
    packages=setuptools.find_packages(),
    install_requires=["setuptools"],
    zip_safe=False,

    include_package_data=True,

)
