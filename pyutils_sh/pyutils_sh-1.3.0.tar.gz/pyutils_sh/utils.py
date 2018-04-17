"""
Utility functions for general purpose Python programming.
"""

import os
import sys


def get_path(f=sys.argv[0]):
    """
    Get path to, and name of, a file.
    
    Parameters
    ----------
    f : str, optional
        Full path to a file. Defaults to the currently executing Python file.
        
    Returns
    -------
    directory : str
        Path to the directory containing the file.
    filename : str
        Name of the file.
    """
    
    return os.path.split(f)
