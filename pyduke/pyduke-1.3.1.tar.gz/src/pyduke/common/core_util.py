import numpy as np
from datetime import datetime
from functional import seq

HR_WIDTH = 50

DATE_TIME_FORMAT = '%a, %d-%b-%Y  %H:%M:%S %p'

def main ():
    A = np.array([[1, 2, 3, 4], [11, 12, 13, 14], [10, 7, 13, 9]])
    print (index_of(A, 11, axis=1))

def hr (size=HR_WIDTH):
    '''Draw a horizontal line of given ``size``'''
    print("-" * size)    

def heading (mesg, size=HR_WIDTH):
    ''' A heading has ``mesg`` with horzintal rule above and below.'''
    print("")
    print("-" * size)
    print(mesg)
    print("-" * size)
    
def join (*mesg, delimiter=" "):
    ''' Join any number of messages ``mesg`` with ``delimiter`` '''
    return delimiter.join (seq(mesg).filter(lambda x: x != None).to_list())

def now():
    ''' Current time '''
    return datetime.now().strftime(DATE_TIME_FORMAT)

def to_2d (X):
    ''' Convert an array or numpy array that is 1d to a row vector that is 2d '''
    return X if (type(X) == np.ndarray and len(X.shape) == 2) else np.array(X).reshape(1, -1)
    
def to_list (x):
    ''' Convert ``x`` to a list. Raise expection if not possible. '''
    if type(x) is tuple or type(x) is list:
        return list(x)
    raise 'InvalidArgumentError: Argument "x" has to be of a type convertable to list using list(<item>), Valid types are "list", "tuple" or "set" Found={}'.format(type(x))

def index_of (X, val, axis=1):
    '''
    If axis is 1 the array is parsed column vice else row vice.
    If 'val' is found the index of the first occurrence is added to list
    '''
    
    # Each column of X is scanned for 'val' (By default axis=1)
    X = to_2d(X)
    X = X.T if axis == 1 else X   
    
    # Count of rows
    m = X.shape[0]
    
    # np.where returns two tuples of same length. 
    # First has the x-coordinates and second has y-coordiantes
    # Each (x,y) shall indicate the position in the matrix where the condition (passed to np.where) is True
    
    # Each element in 'c' tells which column we are talking about
    # Corresponding element in 'r' tells which row of that column has 'val'
    c,r = np.where(X == val)
    search = np.full((1,m), -1)     
    for i in range(len(c)):
        if search[0][c[i]] == -1:
            search[0][c[i]] = r[i]
    return search

if __name__ == '__main__':
    main()    