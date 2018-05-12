"""Setup script
"""
from setuptools import setup

setup(
	   name="sentient_typer",
	   version="1.1.0",
	   description="Print text as if it is being typed by the computer",
	   author="Abhishek Patel",
	   author_email="apbytes@gmail.com",
	   url="https://github.com/Abhishek8394/sentient_typer",
	   license="GPLv2",
	   packages=["sentient_typer"],
	   zip_safe=False,
	   entry_points={
            'console_scripts': ['sentient=sentient_typer.terminal_typer:main']
      },
      long_description_content_type="text/markdown",
      keywords="typing terminal AI terminator"
)
