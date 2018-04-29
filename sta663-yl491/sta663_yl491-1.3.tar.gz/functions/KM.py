import random
import numpy as np
from numba import jit
from helper_functions import distance_speed_multi, distance_index_multi_speed


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