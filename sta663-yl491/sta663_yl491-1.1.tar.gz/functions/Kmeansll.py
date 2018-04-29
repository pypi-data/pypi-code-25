import random
import numpy as np
from numba import jit
from helper_functions import distance_speed_multi, distance_index_multi_speed

@jit
def Kmeansll_speed(k,l,X):
    """
    K-means II Initialization Algorithm
    
    Parameters
    ----------
    k: the number of clusters
    l: the oversample factor
    X: input dataset, matrix of size m x n
    
    Returns
    -------
    C: Centroids initialized for K-means algorithm
    """

    c= np.random.choice(X.shape[0], 1)
    C = X[c]
    psi=sum(distance_speed_multi(X,C))  
   
    for i in range(int(round(np.log(psi)))):
        dist_x=distance_speed_multi(X,C)
        prob=(np.array(dist_x)*l)/np.sum(dist_x)  
        cc=X[np.random.binomial(1,p=prob)==1,:]
        C=np.vstack((C,cc))
    
    C_a=C
    
    index_total=distance_index_multi_speed(X,C_a)
    mat=np.zeros((len(X),len(C)))
    mat[np.arange(len(X)),index_total]=1
    mat_c=np.sum(mat,axis=0)
    
    weight=mat_c/sum(mat_c)    

    return KmeansPP_speed_weighted(C,k,weight=weight)