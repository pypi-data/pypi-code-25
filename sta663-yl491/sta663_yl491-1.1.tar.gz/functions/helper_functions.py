import numpy as np
import random
import numpy.linalg as la
from numba import jit

@jit
def euclidean_dist(a,b):
    """
    Measures the euclidean distance between two vectors.
    
    Parameters
    ----------
    a: array of size 1 x n
    b: array of size 1 x n
    
    Returns
    -------
    The euclidean distance between two points
    """   
    return la.norm(a-b)

@jit
def distance_speed(x,Y):
    """
    Measures the distance between a vector and multiple vectors.
    
    Parameters
    ----------
    x: array of size 1 x n
    Y: matrix of size m x n
    
    Returns
    -------
    The minimum distance from x to one vector in Y
    """   
    dif=x-Y
    su=np.sum(dif**2,axis=1)
    return np.sqrt(np.min(su))

@jit
def distance_speed_multi(X,Y):
    """
    Measures the distance between 2 matices.
    
    Parameters
    ----------
    x: array of size m x n
    Y: matrix of size p x n
    
    Returns
    -------
    An array of size n, the minimum euclidean distance from each vector in X to a vector in Y
    """   
    d=X[:,None]-Y
    su=np.sum(d**2,axis=2)
    return np.sqrt(np.min(su,axis=1))

@jit
def distance_index_speed(x,Y):
    """    
    Parameters
    ----------
    x: array of size 1 x n
    Y: matrix of size m x n
    
    Returns
    -------    
    The index of a row in Y, which has the smallest euclidean distance to x.
    """
    dif=x-Y
    su=np.sum(dif**2,axis=1)
    return np.argmin(su)

@jit
def distance_index_multi_speed(X,Y):
    """    
    Parameters
    ----------
    x: array of size m x n
    Y: matrix of size p x n
    
    Returns
    -------   
    An array of size n, which contains the index of each row in Y, which has the smallest euclidean distance to each row in X.
    """
    d=X[:,None]-Y
    su=np.sum(d**2,axis=2)
    return np.argmin(su,axis=1)