#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 08:29:19 2018

@author: zxs107020
"""

import sys
from .zxs import local_import, transform
import json
import pandas as pd

def main():
    
    # Show stage in program
    sys.stdout.write("Setting directories...")
    sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.flush()
    
    # Read system inputs
    
    # Working directory
    wd = str(sys.argv[1])
    
    # In-file
    fn = str(sys.argv[2])

    # System arguments
    kwargs = json.loads(sys.argv[3])
    
    out = str(sys.argv[4])
    
    # Display process in console
    sys.stdout.write("Loading Data...")
    sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.flush()
    
    # Load the data
    data = local_import(wd, fn)
    
    # Display process in console
    sys.stdout.write("Transforming Data...")
    sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.flush()
    
    # Transform to numeric
    transform(data, **kwargs)
    
    # Display process in console
    sys.stdout.write("Writing file...")
    sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.flush()
    
    # Out-file
    data.to_csv(out)

    # Display process in console
    sys.stdout.write("Process Complete")
    sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.flush()

# Final invocation
if __name__ == '__main__':
    main()    