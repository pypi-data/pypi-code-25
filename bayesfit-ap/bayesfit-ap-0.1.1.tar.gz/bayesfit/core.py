from __future__ import division, print_function

import numpy as np
from scipy.optimize import minimize

def maximize_likelihood(L,x0,args=()):
    '''
    Maximizes the given likelihood function L(x0,*args) starting from
    the initial guess x0. Returns the optimal x with the negative inverse
    of the Hessian of L (i.e. the covariance matrix).
    '''

    #Define the negative of L for minimization
    def negL(x0,*args):
        return -L(x0,*args)

    #Optimize using a robust algorithm
    initial_method = 'Nelder-Mead' #TODO: Could brute force be an option?

    res_initial = minimize(negL,x0,args,initial_method)
    if not res_initial.success:
        raise Exception('Initial optimization failed: ' + res_initial.message +
                        '\nConsider adjusting the initial guess.')

    #Optimize using BFGS
    res = minimize(negL,res_initial.x,args,'BFGS')
    if not res.success:
        print('WARNING! BFGS optimization failed: ' + res.message + '\n' +
                        'Continueing with the '+ initial_method + ' solution.')
        res = res_initial

    #Apparently in at least some versions of scipy, the inverse Hessian given
    #by the BFGS minimization is incorrect. Thus the inverse of hessian is
    #calculated separately here

    def L1(x):
        return L(x,*args)

    H = hessian(L1,res.x)

    return res.x, -np.linalg.inv(H)

def hessian(f,x0,epsilon = 1e-5):
    '''
    Computes the Hessian of f(x) at x0 numerically using finite differences.
    '''

    H = np.zeros((x0.size,x0.size))

    for i in range(x0.size):
        for j in range(x0.size):
            dx1 = np.zeros(x0.shape)
            dx2 = np.zeros(x0.shape)

            dx1[i] = epsilon
            dx2[j] = epsilon

            H[i,j] = (f(x0+dx1+dx2)-f(x0+dx1-dx2)-f(x0-dx1+dx2)+f(x0-dx1-dx2))/(4*epsilon*epsilon)

    return H
