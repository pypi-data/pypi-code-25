import numpy as np

def k_means_int(k,data,radom_state=42):
     #initialization select random centroids:     
    X = data
    rng = np.random.RandomState(radom_state)
    i = rng.permutation(X.shape[0])[:k]
    C = X[i]
    return C