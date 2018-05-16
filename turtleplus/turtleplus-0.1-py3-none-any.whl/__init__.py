"""
The turtle-plus Library

An upgraded version of the "turtle" with a bit of new features.
"""
import sys

if sys.version_info[0] < 3 or (
        sys.version_info[0] == 3 and sys.version_info[1] < 6):
    sys.exit("The Library requires Python 3.6 or higher.")


# import
from turtleplus.draw import *