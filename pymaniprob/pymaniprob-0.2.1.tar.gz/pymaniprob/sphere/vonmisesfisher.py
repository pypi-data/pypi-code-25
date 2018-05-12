import numpy as np
from pymaniprob.probabilitydistributions import MultivariateProbabilityDistribution
from scipy.special import iv, gamma
twopi = 2*np.pi
"""
Class definitions
"""
class BaseVonMisesFisher(MultivariateProbabilityDistribution):
    def __init__(self, m, k, p, **kwargs):
        self.m = m
        self.k = k
        self.p = p
        super(BaseVonMisesFisher, self).__init__(dim=p, **kwargs)


class FrozenVonMisesFisher(BaseVonMisesFisher):

    def __init__(self, m, k, p):
        
        norm_const = k**(p/2 - 1)
        norm_const = norm_const/(iv(p/2-1, k)*twopi**(p/2))

        self.norm_const = norm_const
        self.log_norm_const = np.log(self.norm_const)

        def _pdf(x):
            exp_arg = self.k*np.dot(self.m, x)
            return np.exp(exp_arg)*self.norm_const

        def _logpdf(x):
            exp_arg = self.k*np.dot(self.m, x)
            return exp_arg + self.log_norm_const
        
        super(FrozenVonMisesFisher, self).__init__(m=m, k=k, p=p,
                                                   _pdf=_pdf,
                                                   _logpdf=_logpdf)

    def rvs(self, size=1):
        if self.p == 3:
            return _vmf_rv_S2(self.m, self.k, size)
        elif self.p == 4:
            return _vmf_rv_S3(self.m, self.k, size)


class VonMisesFisher:

    def __new__(self, m=None, k=1, p=2):
        m, k, p = _handle_parameter_specification(m, k, p)
        return FrozenVonMisesFisher(m=m, k=k, p=p)

    @classmethod
    def pdf(self, x, m=None, k=None, p=None, normalised=True):

        def _updf(x):
            return np.exp(k*np.dot(m, x))

        if normalised:
            norm_const = (0.5*k)**(p/2 - 1)
            norm_const /= (gamma(p/2)*iv(p/2-1, k))
            return _updf(x)*norm_const

        else:
            return _updf(x)

    @classmethod
    def rvs(self, m=None, k=1., p=None, size=1):

        if sum([item is not None for item in [m, p]]) == 0:
            msg = "One of 'm' and 'p' must be supplied."
            raise ValueError(msg)

        if m is None and p is not None:
            m = np.eye(N=1, M=p, k=p-1).ravel()
        
        if p == 3:
            rv = _vmf_rv_S2(m, k, size)
            if size == 1:
                return rv.ravel()
            else:
                return rv

        elif p == 4:
            rv = _vmf_rv_S3(m, k, size)
            if size == 1:
                return rv.ravel()
            else:
                return rv
        
        


"""
Utility methods for setting up
"""
def _handle_parameter_specification(m, k, p):
    _norm_tol = 1e-5
    
    if m is None:
        m = np.zeros(p)
        m[0] = 1.
    else:
        m = np.asarray(m)
        try:
            assert( abs(np.linalg.norm(m) - 1.) < _norm_tol)
        except:
            raise ValueError("mean should be a unit vector")
        assert(m.size == p)

    return m, k, p


"""
Acceptance-Rejection sampling methods for the auxillary
distribution

in general this distribution is of the form

p(t) propto exp(k*t)*(1-t^2)^((p-3)/2)

"""

# For the case p=4
def _t_4_ar(k, size=1):

    def _up(t, k):
        return np.exp(k*t)*np.sqrt(1-t**2)

    t_mode = 0.5*(np.sqrt(4*k**2 + 1)-1)/k
    pmode = _up(t_mode, k)

    count = 1
    max_count = 1000

    res = np.array([])
    while True:
        z = np.random.uniform(-1, 1, size=size)
        pz = _up(z, k)
        u = np.random.uniform(0, pmode, size=size)

        # Store the accepted points
        z_acc = z[u <= pz]
        res = np.concatenate((res, z_acc))

        # Remaining number to sample
        size -= z_acc.size

        if size == 0:
            return res
        else:
            count += 1
            if count >= max_count:
                break    

"""
Von Mises Fisher simulation methods
"""
def _vmf_rv_S2_npole(k, size=1):
    U = np.random.uniform(size=size)
    cos_theta_rv = np.log(np.exp(k) - U*2*np.sinh(k))/k

    theta = np.arccos(cos_theta_rv)
    phi = np.random.uniform(size=size)*2*np.pi

    z = np.cos(theta)
    y = np.sin(theta)*np.cos(phi)
    x = np.sin(theta)*np.sin(phi)

    return np.column_stack((x, y, z))

def _vmf_rv_S2(m, k, size=1):
    rv = _vmf_rv_S2_npole(k, size=size)

    v2 = np.random.normal(size=3)
    v3 = np.random.normal(size=3)

    u2 = v2 - proju(v2, m)
    u2 /= np.linalg.norm(u2)

    u3 = v3 - proju(v3, m) - proju(v3, u2)
    u3 /= np.linalg.norm(u3)

    O = np.column_stack((u3, u2, m))

    return np.array([np.dot(O, x) for x in rv])

def _vmf_rv_S3_npole(k, size=1):

    ts = _t_4_ar(k, size)

    expr = np.sqrt(1-ts**2)
    xis = np.random.normal(size=size*3).reshape(size, 3)
    xis = np.array([item*xi/np.linalg.norm(xi)
                    for item, xi in zip(expr, xis)])

    xis = np.column_stack((xis, ts))

    return xis

def _vmf_rv_S3(m, k, size=1):

    # Generate rv with mean [0., 0., 0., 1]
    rv = _vmf_rv_S3_npole(k, size=size)

    v2 = np.random.normal(size=4)
    v3 = np.random.normal(size=4)
    v4 = np.random.normal(size=4)

    u2 = v2 - proju(v2, m)
    u2 /= np.linalg.norm(u2)

    u3 = v3 - proju(v3, m) - proju(v3, u2)
    u3 /= np.linalg.norm(u3)

    u4 = v4 - proju(v4, m) - proju(v4, u2) - proju(v4, u3)
    u4 /= np.linalg.norm(u4)

    O = np.column_stack((u4, u3, u2, m))

    return np.array([np.dot(O, x) for x in rv])


"""
Linear algebra utility functions
"""

# Projection of the vector v onto u
def proju(v, u):
    return np.dot(u, v)*u/np.dot(u, u)
