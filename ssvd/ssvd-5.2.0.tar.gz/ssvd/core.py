import numpy as np
import math
from numba import jit

@jit
def thresh_jit(z,delta):
    return np.sign(z)*(np.abs(z) >= delta)*(np.abs(z)-delta)

def ssvd(X, gamma_u = 2, gamma_v = 2, merr = 10**(-4), niter = 100):
    #rank 1
    U,s,V = np.linalg.svd(X)#initial svd
    u0 = U.T[0] 
    v0 = V.T[0]

    n=X.shape[0]
    d=X.shape[1]
    ud = 1
    vd = 1
    iters = 0
    SST = np.sum(X*X)

    while (ud > merr or vd > merr):
        iters = iters + 1

        #update v
        z=X.T @ u0#initial OLS estimator (of the coefficients)
        w_v_inv=np.abs(z) ** gamma_v#inverse of adapative weight 
        sig_sq=np.abs(SST-np.sum(z*z))/(n*d-d)#OLS estimate of the error variance
        tmp=z*w_v_inv
        tv=np.unique(np.sort(np.append(np.abs(tmp),0)))#possible lambda set
        Bv = np.ones(len(tv)-1)*np.Inf
        index=np.where(w_v_inv>10^-8)
        tmp1=tmp[index]
        w_v_inv1=w_v_inv[index]
        for i in range(len(Bv)):
            temp2 = thresh_jit(tmp1,delta = tv[i])
            temp2 = temp2/w_v_inv1
            temp3 = np.zeros(d)
            temp3[index] = temp2
            Bv[i] = np.sum((X - u0[:,None] @ temp3[None,:])**2)/sig_sq + np.sum(temp2!=0)*math.log(n*d)
        Iv = min(np.where(Bv== np.min(Bv)))
        th = tv[Iv]
        temp2 = thresh_jit(tmp1,delta = th)
        temp2 = temp2/w_v_inv1
        v1 = np.zeros(d)
        v1[index] = temp2
        v1 = v1/((np.sum(v1*v1))**0.5) #v_new

        #update v
        z=X @ v1#initial OLS estimator (of the coefficients)
        w_u_inv=np.abs(z) ** gamma_u#inverse of adapative weight 
        sig_sq=np.abs(SST-np.sum(z*z))/(n*d-n)#OLS estimate of the error variance
        tmp=z*w_u_inv
        tv=np.unique(np.sort(np.append(np.abs(tmp),0)))#possible lambda set
        Bu = np.ones(len(tv)-1)*np.Inf
        index=np.where(w_u_inv>10^-8)
        tmp1=tmp[index]
        w_u_inv1=w_u_inv[index]
        for i in range(len(Bu)):
            temp2 = thresh_jit(tmp1,delta = tv[i])
            temp2 = temp2/w_u_inv1
            temp3 = np.zeros(n)
            temp3[index] = temp2
            Bu[i] =  np.sum((X - temp3[:,None] @ v1[None,:])**2)/sig_sq + np.sum(temp2!=0)*math.log(n*d)
        Iu = min(np.where(Bu== np.min(Bu)))
        th = tv[Iu]
        temp2 = thresh_jit(tmp1,delta = th)
        temp2 = temp2/w_u_inv1
        u1 = np.zeros(n)
        u1[index] = temp2
        u1 = u1/((np.sum(u1*u1))**0.5) #u_new

        ud = np.sum((u0-u1)*(u0-u1))**0.5
        vd = np.sum((v0-v1)*(v0-v1))**0.5

        if iters > niter :
            print("Fail to converge! Increase the niter!")
            break

        u0 = u1
        v0 = v1

    s = u1[None, :] @ X @ v1[:, None]
    return u1, v1, s, iters