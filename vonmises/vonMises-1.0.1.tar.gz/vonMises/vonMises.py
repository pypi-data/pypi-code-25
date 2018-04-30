
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import scipy.integrate as integrate
from scipy.optimize import brentq as root
import math
import numpy as np
import scipy.special as scp
from scipy.special import iv


# In[2]:


def rvonmises(n, mu, kappa):
    vm = np.zeros(n)
    a = 1 + (1 + 4 * (kappa**2))**0.5
    b = (a - (2 * a)**0.5)/(2 * kappa)
    r = (1 + b**2)/(2 * b)
    obs = 0
    while (obs < n):
        U1 = np.random.uniform(0, 1, 1)
        z = np.cos(np.pi * U1)
        f = (1 + r * z)/(r + z)
        c = kappa * (r - f)
        U2 = np.random.uniform(0, 1, 1)
        if (c * (2 - c) - U2 > 0):
            U3 = np.random.uniform(0, 1, 1)
            vm[obs] = np.sign(U3 - 0.5) * math.acos(f) + mu
            vm[obs] = vm[obs] % (2 * np.pi)
            obs = obs + 1
        else:
            if (math.log(c/U2) + 1 - c >= 0):
                U3 = np.random.uniform(0, 1, 1)
                vm[obs] = np.sign(U3 - 0.5) * math.acos(f) + mu
                vm[obs] = vm[obs] % (2 * math.pi)
                obs = obs + 1
    return(vm)


# In[3]:


def dvonmises(x, mu, kappa, log = False):
    if (type(x) == int):
        x = [x]
    if (type(x) == float):
        x = [x]
    vm = np.zeros(len(x))
    if (log):
        if (kappa == 0):
            vm = np.log(np.repreat(1/(2*pi), len(x)))
        elif (kappa < 100000):
            vm = -(np.log(2*math.pi)+np.log(scp.ive(0, kappa)) + kappa) + kappa*(np.cos(np.subtract(x - mu)))
        else:
            if (((x-mu)%(2*math.pi))==0):
                vm = math.inf
            else:
                vm = -math.inf
    else:
        if (kappa == 0):
            vm = np.repeat(1/(2*np.pi), len(x))
        elif (kappa < 100000):
            vm = 1/(2 * np.pi * scp.ive(0, kappa)) * (np.exp(np.subtract(np.cos(np.subtract(x, mu)), 1)))**kappa
        else:
            if (np.mod(np.subtract(x, mu),(2*np.pi))==0):
                vm = math.inf
            else:
                vm = 0
    return(vm)


# In[21]:


def pvonmises(q, mu, kappa, tol = 1e-020):
    from_ = mu - np.pi
    mu = (mu - from_) % (2 * np.pi)
    if (type(q) == int):
        q = [q]
    if(type(q) == float):
        q =[q]
    q = np.mod(np.subtract(q, from_), (2 * np.pi))
    q = np.mod(q,(2 * np.pi))
    n = len(q)
    mu = mu % (2 * np.pi)
    def pvm_mu0(q, kappa, tol):
        flag = True
        p = 1
        sum_ = 0
        while (flag):
            term = (iv(p, kappa) * np.sin(np.multiply(q, p)))/p
            sum_ = sum_ + term
            p = p + 1
            if (abs(term) < tol):
                flag = False
        return(np.divide(q,(2 * np.pi)) + sum_/(np.pi * iv(0, kappa)))

    result = np.repeat(np.nan, n)
    if (mu == 0):
        for i in range(0,n):
            result[i] = pvm_mu0(q[i], kappa, tol)
    else:
        for i in range(0,n):
            if (q[i] <= mu):
                upper = (q[i] - mu) % (2 * np.pi)
                if (upper == 0):
                    upper = 2 * np.pi
                lower = (-mu) % (2 * np.pi)
                result[i] = pvm_mu0(upper, kappa, tol) - pvm_mu0(lower, kappa, tol)
            else:
                upper = q[i] - mu
                lower = mu % (2 * np.pi)
                result[i] = pvm_mu0(upper, kappa, tol) + pvm_mu0(lower, kappa, tol)
    return(result)


# In[63]:


def qvonmises(p, mu = 0 ,  kappa = None, from_ = None, tol = np.finfo(float).eps**0.6):
    epsilon = 10 * np.finfo(float).eps     ##epsilon is Python equivalent of .Machine$double.eps
    if (type(p) == int):
        p = np.array([p])
    elif (type(p) == float):
        p = np.array([p])
    else:
        p = np.array(p)
    if (np.any(p > 1)): 
        raise ValueError("p must be in [0,1]")
    elif (np.any(p < 0)):
        raise ValueError("p must be in [0,1]")

    if (pd.isnull(from_)): ##from is a keyword
        from_ = mu - np.pi
   
    n = p.size
    mu = (mu - from_)%(2 * np.pi)      ## from is a keyword    
    if (pd.isnull(kappa)): 
        raise ValueError("kappa must be provided")   
        
    def zeroPvonmisesRad(x, p, mu, kappa):
        if (np.isnan(x)):         
            y = np.nan              
        else: 
            integration = integrate.quad(lambda x: dvonmises(x, mu, kappa), 0, x)
            y = integration[0] - p         ##integration[0] will give the value
        return(y);
    
    value = np.repeat(np.nan, p.size)
    for i in range(p.size):
        try:
            value[i] = root(lambda x: zeroPvonmisesRad(x, p[i], mu, kappa), 0, 2 * np.pi - epsilon)
        except:
            pass
            if(p[i] < (10 * epsilon)):
                value[i] = 0
            elif (p[i] > (1 - 10 * epsilon)):
                value[i] = 2 * np.pi - epsilon         
    value += from_
    return(value)

