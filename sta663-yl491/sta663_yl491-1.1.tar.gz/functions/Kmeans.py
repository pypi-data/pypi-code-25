import random
import numpy as np
from numba import jit
from helper_functions import distance_index_multi_speed

@jit
def Kmeans_speed(C,X,k,initial=False):
    """
    K-means algorithm implementation
    
    Parameters
    ----------
    C: initial centroids, size k x n
    X: dataset, size m x n
    k: number of centroids desired
    initial: Boolean value; True = use input centroids, 
                            False = use random initialization, which is original Kmeans initialization
    
    Returns:
    --------
    C0: the final centroids, size k x n
    X_C: the index of center that each vector x belongs to; size m x 1
    """
    
    if initial:
        C0=C
    else:
        C0=X[np.random.choice(range(X.shape[0]),k)]  
    convergence=False
    
    m=0
    X_C1=np.zeros(len(X))
    X_C=np.zeros(len(X))
    while not convergence:
        X_C1=X_C
        X_C=distance_index_multi_speed(X,np.squeeze(np.asarray(C0)))
        for i in range(0,len(C0)):
            X_Ci=X[np.where(X_C==i)]
            if np.sum(X_C==i)!=0:
                C0[i]=np.mean(X_Ci,axis=0)
        convergence=np.array_equal(X_C,X_C1)

        m=m+1
        if m>1000:
            break
    return C0,X_C,m   