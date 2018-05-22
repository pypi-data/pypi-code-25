from setuptools import setup, find_packages

setup(
    name="ckenchanter",
    version="1.2.0",
    packages=find_packages(),
    install_requires=(
        "pyenchant",
    ),
    author="Charley Bodkin and James Perez",
    author_email="charley@bodkin.me, jdperez04@gmail.com",
    description="Extends the PyEnchant library for use in a CKEditor spellcheck server.",
    long_description="Extends the PyEnchant library to parse requests from CKEditor's spellchecker and return suggested corrections using standard language dictionaries and custom personal word lists.",
    url="https://github.com/jperezlatimes/ckenchanter",
    license="GNU GENERAL PUBLIC LICENSE",
)
