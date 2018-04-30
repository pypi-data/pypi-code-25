import numpy as np
from pkg.dist import dist

def kmeanspp(k, X, random_state=42):
    # generate centers
    rs = np.random.RandomState(random_state)
    C = X[rs.randint(len(X)),:].reshape(1,X.shape[1])
    while C.shape[0] <= k-1:
        distances =np.array([min([dist(c,x,0) for c in C]) for x in X])
        #calculate the probability of centers
        prob = distances/distances.sum()
        cumprob = np.cumsum(prob)
        r = np.random.random_sample()
        #get the indice for the next cnter
        indice = min(np.where(cumprob >= r))[0]
        nc = X[indice].reshape(1,X.shape[1])
        C = np.append(C,nc,axis=0)
    
    return C