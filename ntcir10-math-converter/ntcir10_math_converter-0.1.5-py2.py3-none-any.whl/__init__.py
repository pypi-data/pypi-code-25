"""
The NTCIR-10 Math Converter package converts NTCIR-10 Math dataset and
relevance judgements to the NTCIR-11 Math-2, and NTCIR-12 MathIR format.
"""

from .converter import convert_judgements, get_judged_identifiers, process_dataset
from .__main__ import main


__author__ = "Vit Novotny"
__version__ = "0.1.5"
__license__ = "MIT"
