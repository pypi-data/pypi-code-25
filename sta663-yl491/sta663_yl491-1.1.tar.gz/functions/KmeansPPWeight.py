import random
import numpy as np
from numba import jit
from helper_functions import distance_speed_multi

@jit
def KmeansPP_speed_weighted(X,k,weight):
    """
    K-means ++ Initialization with Weight Input, used in K-means ll Initialization
    
    Parameters
    ----------
    X: matrix of size m x n
    k: number of centers desired
    weight: array of size m x 1
    
    Returns
    -------    
    C: the centroids initialized
    """
    random.seed(28)

    c=np.random.randint(0,len(X),1)
    C=X[c]
    dist2=weight*distance_speed_multi(X,C)
    probability=dist2/np.sum(dist2)
    
    while(len(C)<k):
        cc=np.random.choice(len(X), size=1, p=probability)
        C=np.vstack((C,X[cc]))
            
        dist2=weight*distance_speed_multi(X,np.squeeze(np.array(C)))
        probability=dist2/np.sum(dist2)

    return C
