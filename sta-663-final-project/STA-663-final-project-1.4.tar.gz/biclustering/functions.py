import numpy as np
from sparsesvd import sparsesvd 
from scipy.sparse import csc_matrix
import seaborn as sns; sns.set()

def SSVD_python(X, gamma1 = 2, gamma2 = 2, tol = 1e-4, max_iter = 100):
    """SSVD for first layer with python optimization
    
    X = data matrix
    gamma1, gamma2 = weight parameters, default set to 2
    tol = tolerance for convergence, default set to 1e-4
    max_iter = maximum number of iterations, default set to 100
    
    If converged, return:
    
    u = u vector of Sparse SVD
    s = largest singular value from SVD
    v = v vector of Sparse SVD
    niter = number of iteration until convergence
    
    If not converged, print:
    
    "Fail to converge! Increase the max_iter!"
    
    Example usage:
    
    u, s, v, niter = SSVD_primary(X)    
    """
    u, s, v = sparsesvd(csc_matrix(X), k=1)
    
    # initializations
    n = X.shape[0]
    d = X.shape[1]
    u = u.reshape((n,1))
    v = v.reshape((d,1))
    u_delta = 1
    v_delta = 1
    niter = 0
    SST = np.sum(X**2)
    
    while((u_delta > tol) or (v_delta > tol)):
        niter += 1

        # update v
        Xu = X.T @ u
        w2_inv = np.abs(Xu)**gamma2
        sigma_sq = np.abs(SST - sum(Xu**2))/(n*d-d)   #np.trace((X-s*u@v.T) @ (X-s*u@v.T).T)/(n*d-d)

        lambda2s = np.unique(np.append(np.abs(Xu*w2_inv), 0))
        lambda2s.sort()                                   # possible lambda2/2

        # best BIC
        BICs = np.ones(lambda2s.shape[0]-1)*np.Inf
        for i in range(BICs.shape[0]):
            v_temp = np.sign(Xu)*(np.abs(Xu) >= lambda2s[i] / w2_inv)*(np.abs(Xu) - lambda2s[i] / w2_inv)
            BICs[i] = np.sum((X-u@v_temp.T)**2)/sigma_sq + np.sum(v_temp!=0)*np.log(n*d)
        best = np.argmin(BICs)

        lambda2 = lambda2s[best]
        v_new = np.sign(Xu)*(np.abs(Xu) >= lambda2 / w2_inv)*(np.abs(Xu) - lambda2 / w2_inv)
        v_new = v_new/np.sqrt(np.sum(v_new**2))

        v_delta = np.sqrt(np.sum((v-v_new)**2))
        v = v_new


        # update u
        Xv = X @ v
        w1_inv = np.abs(Xv)**gamma1
        sigma_sq = np.abs(SST - sum(Xv**2))/(n*d-n) 

        lambda1s = np.unique(np.append(np.abs(Xv*w1_inv), 0))
        lambda1s.sort()                                   # possible lambda1/2

        # best BIC
        BICs = np.ones(lambda1s.shape[0]-1)*np.Inf
        for i in range(BICs.shape[0]):
            u_temp = np.sign(Xv)*(np.abs(Xv) >= lambda1s[i] / w1_inv)*(np.abs(Xv) - lambda1s[i] / w1_inv)
            BICs[i] = np.sum((X-u_temp@v.T)**2)/sigma_sq + np.sum(u_temp!=0)*np.log(n*d)
        best = np.argmin(BICs)

        lambda1 = lambda1s[best]
        u_new = np.sign(Xv)*(np.abs(Xv) >= lambda1 / w1_inv)*(np.abs(Xv) - lambda1 / w1_inv)
        u_new = u_new/np.sqrt(np.sum(u_new**2))

        u_delta = np.sqrt(np.sum((u-u_new)**2))
        u = u_new

        # check iterations
        if niter > max_iter:
            print("Fail to converge! Increase the max_iter!")
            break
    return(np.ravel(u), s, np.ravel(v), niter)
    
    
def plotClusters(u, s, v, group, tresh):
    """Plotting Clusters for rank 1 approximation
    
    u, s, v = return values of SSVD function
    group = vector of known groups, None if no grouping is known
    tresh = value for discarding insignificant rows.
    
    return:
    Heatmap of rank 1 approximated clusters
    
    Example usage:
    
    u, s, v, niter = SSVD_primary(X)
    plotClusters(u,s,v,None,0)
    """
    first = s*u.reshape((-1, 1))@v.reshape((1, -1))

    groups = np.unique(group)
    row_idx = np.empty(0, dtype = 'int')
    for i in range(len(groups)):
        idx, = np.where(group == groups[i])
        idx_ = idx[np.argsort(u[idx])]
        row_idx = np.concatenate((row_idx, idx_))

    col_nonzero = np.argsort(np.abs(v))[tresh:]
    v_nonzero = v[col_nonzero]
    first_nonzero = first[:,col_nonzero]
    col_idx = np.argsort(v_nonzero)

    ax = sns.heatmap(first_nonzero[np.ix_(row_idx, col_idx)], vmin=-1, vmax=1, cmap = 'bwr')