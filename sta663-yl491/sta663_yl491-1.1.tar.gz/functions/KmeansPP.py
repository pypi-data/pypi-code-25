import random
import numpy as np
from numba import jit
from helper_functions import distance_speed_multi

@jit
def KmeansPP_speed(X,k):
    """
    K-means++ Initialization
    
    Parameters
    ----------
    X: matrix of m x n
    k: number of centers desired
    
    Returns
    -------
    C: an matrix of size k x n, containing the centroids initialized by K-means++ Algorithm
    """
    random.seed(28)
    #starting with a randomly selected point.
    c=np.random.randint(0,len(X),1)
    C=X[c]
    
    dist2=distance_speed_multi(X,C)
    probability=dist2/np.sum(dist2)
    
    while(len(C)<k):
        cc=np.random.choice(len(X), size=1, p=probability)
        C=np.vstack((C,X[cc]))
            
        dist2=distance_speed_multi(X,C)
        probability=dist2/np.sum(dist2)

    return C