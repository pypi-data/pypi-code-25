import os
import numpy as np
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HR_WIDTH = 50

DATE_TIME_FORMAT = '%a, %d-%b-%Y  %H:%M:%S %p'

def hr (size=HR_WIDTH):
    '''Draw a horizontal line of given size'''
    print("-" * size)    

def heading (mesg, size=HR_WIDTH):
    print("")
    print("-" * size)
    print(mesg)
    print("-" * size)
    
def join (*mesg_list, delimiter=" "):
    _list = [ x for x in mesg_list if x != None ]    
    return delimiter.join (_list)

def now():
    return datetime.now().strftime(DATE_TIME_FORMAT)

def to_2d (X):
    return X if (type(X) == np.ndarray and len(X.shape) == 2) else np.array(X).reshape(1, -1)
    

