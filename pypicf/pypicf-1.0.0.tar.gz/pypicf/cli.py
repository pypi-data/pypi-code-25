#!/usr/bin/env python
# coding: utf-8

from argparse import (
    ArgumentParser,
    RawDescriptionHelpFormatter
)

description = """PYPI Classifiers for Humans

The pypicf asks you of PYPI Classifiers for setup.py script.
(https://pypi.org/pypi?%3Aaction=list_classifiers)
"""

parser = ArgumentParser(
    prog="pypicf",
    formatter_class=RawDescriptionHelpFormatter,
    description=description)

parser.add_argument(
    "--dev",
    action="store_true",
    help="Run the pypicf to development mode.")
