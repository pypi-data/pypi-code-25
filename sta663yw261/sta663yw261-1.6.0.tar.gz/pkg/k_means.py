import numpy as np
from dist import dist

def k_means(k,X,C,max_iter=10000):
    clusters = np.zeros(len(X))
    C_old = np.zeros(C.shape)
    error = dist(C, C_old, None)
    m=0
    while (error !=0):
        # update cluster groups
        for i in range(len(X)):
                distances = dist(X[i], C)
                cluster = np.argmin(distances)
                clusters[i] = cluster
        
        # update the centroid 
        new_centers = np.array([X[clusters == i].mean(0)
                                for i in range(k)])
        
        # check convergence
        error = dist(C, C_old,None)
        C_old = C
        C= new_centers
        m+=1
        if m > max_iter:
            break
    return (C,clusters,m)