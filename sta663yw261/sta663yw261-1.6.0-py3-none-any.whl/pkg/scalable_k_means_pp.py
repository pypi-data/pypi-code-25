import numpy as np
from dist import dist

def weights_c(X, C):
    w = np.zeros(C.shape[0])
    for i in range(len(X)):
        if i not in C:
            ind = np.argmin([dist(X[i],c,0) for c in C])
            w[ind] +=1
    return w

def weighted_kmeans(Cen,w,k,random_state=42):
    rs = np.random.RandomState(42)
    ran = rs.randint(len(Cen))    
    C1 = Cen[ran,:].reshape(1,Cen.shape[1])
    X1 = np.delete(Cen, ran, 0)
    w = np.delete(w, ran)
    while C1.shape[0] <= k-1:
        #calculate the probability of centers
        prob =w/w.sum()
        cumprob = np.cumsum(prob)
        r = np.random.random_sample()
        #get the indice for the next cnter
        indice = min(np.where(cumprob >= r))[0]
        nc = X1[indice].reshape(1,Cen.shape[1])
        X1 = np.delete(X1, indice, 0)
        w = np.delete(w, indice)
        C1 = np.append(C1,nc,axis=0)
    return C1

def k_meansll(k, X, l, random_state = 42):
    #step 1 random centroid
    rs = np.random.RandomState(random_state)
    C = X[rs.randint(len(X)),:].reshape(1,X.shape[1])
    distances =np.array([min([dist(c,x,0) for c in C]) for x in X])
    phi = distances.sum()
    lgphi = round(np.log(phi))
    prob = l*distances/distances.sum()
    cumprob = np.cumsum(prob)
    i=0
    
    while i < lgphi:
            r = np.random.random_sample()
            #get the indice for the next cnter
            indice = min(np.where(cumprob >= r))[0]
            nc = X[indice].reshape(1,X.shape[1])
            C = np.append(C,nc,axis=0)
            i+=1
    
    w = weights_c(X,C) 
    w_C = weighted_kmeans(C,w,k) 
    return w_C   