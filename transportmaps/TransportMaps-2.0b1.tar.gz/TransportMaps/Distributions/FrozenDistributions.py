#
# This file is part of TransportMaps.
#
# TransportMaps is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TransportMaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with TransportMaps.  If not, see <http://www.gnu.org/licenses/>.
#
# Transport Maps Library
# Copyright (C) 2015-2018 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Authors: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import warnings
import numpy as np
import numpy.linalg as npla
import scipy.stats as stats
import scipy.linalg as scila
import scipy.special as scispec

import SpectralToolbox.Spectral1D as S1D
import SpectralToolbox.SpectralND as SND

from TransportMaps.Misc import counted, cached
from TransportMaps.Distributions.DistributionBase import *
from TransportMaps.Distributions.TransportMapDistributions import *

__all__ = ['FrozenDistribution_1d',
           'GaussianDistribution', 'StandardNormalDistribution',
           'ChainGraphGaussianDistribution',
           'StarGraphGaussianDistribution',
           'GridGraphGaussianDistribution',
           'LogNormalDistribution', 'LogisticDistribution',
           'GammaDistribution', 'BetaDistribution',
           'WeibullDistribution', 'CauchyDistribution',
           'GumbelDistribution', 'BananaDistribution',
           'StudentTDistribution']

nax = np.newaxis

class FrozenDistribution_1d(Distribution):
    r""" [Abstract] Generic frozen distribution 1d
    """
    def __init__(self):
        super(FrozenDistribution_1d,self).__init__(1)
        self.base = StandardNormalDistribution(1)
        self.scipy_base = stats.norm()
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    def quadrature(self, qtype, qparams, mass=1, **kwargs):
        r""" Generate quadrature points and weights.

        Types of quadratures:

        Monte-Carlo (``qtype==0``)
           ``qparams``: (:class:`int`) -- number of samples

        Quasi-Monte-Carlo (``qtype==1``)
           ``qparams``: (:class:`int`) -- number of samples

        Latin-Hypercube-Sampling (``qtype==2``)
           ``qparams``: (:class:`int`) -- number of samples

        Gauss-quadrature (``qtype==3``)
           ``qparams``: (:class:`list<list>` [:math:`d`]) -- orders for
           each dimension

        .. seealso:: :func:`Distribution.quadrature`
        """
        if qtype == 0:
            # Monte Carlo sampling
            x = self.rvs(qparams)
            w = np.ones(qparams)/float(qparams)
        elif qtype == 1:
            # Quasi-Monte Carlo sampling
            raise NotImplementedError("Not implemented")
        elif qtype == 2:
            # Latin-Hyper cube sampling
            raise NotImplementedError("Todo")
        elif qtype == 3:
            # Gaussian quadrature
            (x1,w) = self.base.quadrature(3, qparams, mass=mass)
            x = self.dist.ppf( self.scipy_base.cdf(x1[:,0]) )[:,nax]
        else:
            raise ValueError("Quadrature type not recognized")
        return (x,w)

    @cached(caching=False)
    @counted
    def action_hess_x_log_pdf(self, x, dx, *args, **kwargs):
        return np.einsum('...ij,...j->...i',
                         self.hess_x_log_pdf(x, *args, **kwargs), dx )

#########################################################
# Definitions of Gaussian and Standard normal densities #
#########################################################
class GaussianDistribution(Distribution):
    r""" Multivariate Gaussian distribution :math:`\pi`

    Args:
      mu (:class:`ndarray<numpy.ndarray>` [:math:`d`]): mean vector
      sigma (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): covariance matrix
      precision (:class:`ndarray<numpy.ndarray>` [:math:`d,d`]): precision matrix
    """

    def __init__(self, mu, sigma=None, precision=None):
        if (sigma is not None) and (precision is not None):
            raise ValueError("The fields sigma and precision are mutually " +
                             "exclusive")
        super(GaussianDistribution,self).__init__(mu.shape[0])
        self._mu = None
        self._sigma = None
        self._precision = None
        self.mu = mu
        if sigma is not None:
            self.sigma = sigma
        if precision is not None:
            self.precision = precision

    @property
    def mu(self):
        return self._mu

    @mu.setter
    def mu(self, mu):
        if (self._sigma is not None and mu.shape[0] != self._sigma.shape[0]) or \
           (self._precision is not None and mu.shape[0] != self._precision.shape[0]):
            raise ValueError("Dimension d of mu and sigma/precision must be the same")
        self._mu = mu

    @property
    def sigma(self):
        return self._sigma

    @sigma.setter
    def sigma(self, sigma):
        if self.mu.shape[0] != sigma.shape[0] or self.mu.shape[0] != sigma.shape[1]:
            raise ValueError("Dimension d of mu and sigma must be the same")
        if self._sigma is None or np.any(self._sigma != sigma):
            self._sigma = sigma
            try:
                chol = scila.cho_factor(self._sigma, True) # True: lower triangular
            except scila.LinAlgError:
                # Obtain the square root from svd
                u,s,v = scila.svd(self._sigma)
                self.log_det_sigma = np.sum(np.log(s))
                self.det_sigma = np.exp( self.log_det_sigma )
                self.sampling_mat = u * np.sqrt(s)[np.newaxis,:]
                self.inv_sigma = np.dot(u * (1./s)[np.newaxis,:], v.T)
            else:
                self.det_sigma = np.prod(np.diag(chol[0]))**2.
                self.log_det_sigma = 2. * np.sum( np.log( np.diag(chol[0]) ) )
                self.sampling_mat = np.tril(chol[0])
                self.inv_sigma = scila.cho_solve(chol, np.eye(self.dim))

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, precision):
        if self.mu.shape[0] != precision.shape[0] or self.mu.shape[0] != precision.shape[1]:
            raise ValueError("Dimension d of mu and precision must be the same")
        if self._precision is None or np.any(self.inv_sigma != precision):
            self._precision = precision
            self.inv_sigma = precision
            chol = scila.cho_factor(self.inv_sigma, False) # False: upper triangular
            self.sigma = scila.cho_solve(chol, np.eye(self.dim))
            self.det_sigma = 1. / np.prod(np.diag(chol[0]))**2.
            self.log_det_sigma = - 2. * np.sum( np.log( np.diag(chol[0]) ) )
            self.sampling_mat = scila.solve_triangular(np.triu(chol[0]),
                                                       np.eye(self.dim),
                                                       lower=False)
            
    def rvs(self, m, *args, **kwargs):
        r""" Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- samples

        .. seealso:: :func:`Distribution.rvs`
        """
        z = stats.norm().rvs(m*self.dim).reshape((m,self.dim))
        samples = self._mu + np.dot( self.sampling_mat, z.T ).T
        return samples

    def quadrature(self, qtype, qparams, mass=1., **kwargs):
        r""" Generate quadrature points and weights.

        Types of quadratures:

        Monte-Carlo (``qtype==0``)
           ``qparams``: (:class:`int`) -- number of samples

        Quasi-Monte-Carlo (``qtype==1``)
           ``qparams``: (:class:`int`) -- number of samples

        Latin-Hypercube-Sampling (``qtype==2``)
           ``qparams``: (:class:`int`) -- number of samples

        Gauss-quadrature (``qtype==3``)
           ``qparams``: (:class:`list<list>` [:math:`d`]) -- orders for
           each dimension

        .. seealso:: :func:`Distribution.quadrature`
        """
        if qtype == 0:
            # Monte Carlo sampling
            x = self.rvs(qparams)
            w = np.ones(qparams)/float(qparams)
        elif qtype == 1:
            # Quasi-Monte Carlo sampling
            raise NotImplementedError("Not implemented")
        elif qtype == 2:
            # Latin-Hyper cube sampling
            raise NotImplementedError("Todo")
        elif qtype == 3:
            # Gaussian quadrature
            # Generate first a standard normal quadrature
            # then apply the Cholesky transform
            P = SND.PolyND( [S1D.HermiteProbabilistsPolynomial()] * self.dim )
            (x,w) = P.GaussQuadrature(qparams, norm=True)
            x = np.dot( self.sampling_mat, x.T ).T
            x += self._mu
            # For stability sort in ascending order of w
            srt_idxs = np.argsort(w)
            w = w[srt_idxs]
            x = x[srt_idxs,:]
        else:
            raise ValueError("Quadrature type not recognized")
        w *= mass
        return (x,w)

    @counted
    def pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\pi(x)`

        .. seealso:: :func:`Distribution.pdf`
        """
        return np.exp( self.log_pdf(x) )

    @cached()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\log\pi(x)`

        .. seealso:: :func:`Distribution.log_pdf`
        """
        b = x - self._mu
        sol = np.dot( self.inv_sigma, b.T ).T
        out = - .5 * np.einsum('...i,...i->...', b, sol) \
              - self.dim * .5 * np.log(2.*np.pi) \
              - .5 * self.log_det_sigma
        return out.flatten()

    @cached()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x}\log\pi(x)`

        .. seealso:: :func:`Distribution.grad_x_log_pdf`
        """
        b = x - self._mu
        return - np.dot( self.inv_sigma, b.T ).T

    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x}\log\pi(x)`

        .. seealso:: :func:`Distribution.hess_x_log_pdf`
        """
        return - np.ones(x.shape[0])[:,nax,nax] * self.inv_sigma[nax,:,:]

    @counted
    def action_hess_x_log_pdf(self, x, dx, *args, **kwargs):
        r""" Evaluate :math:`\langle \nabla^2_{\bf x} \log \pi({\bf x}), \delta{\bf x}\rangle`

        .. seealso:: :func:`Distribution.action_hess_x_log_pdf`
        """
        return - np.dot( dx, self.inv_sigma )

    def mean_log_pdf(self):
        r""" Evaluate :math:`\mathbb{E}_{\pi}[\log \pi]`.

        .. seealso:: :func:`Distribution.mean_log_pdf`
        """
        return - .5 * ( self.dim * np.log(2*np.pi) + self.dim + self.log_det_sigma )

class StandardNormalDistribution(GaussianDistribution, ProductDistribution):
    r""" Multivariate Standard Normal distribution :math:`\pi`.

    Args:
      d (int): dimension
    """

    def __init__(self, dim):
        self._mu = np.zeros(dim)
        self._sigma = np.eye(dim)
        self._precision = np.eye(dim)
        self.log_det_sigma = 0.
        self.det_sigma = 1.
        self.sampling_mat = np.eye(dim)
        self.inv_sigma = np.eye(dim)
        Distribution.__init__(self, dim)

    def rvs(self, m, *args, **kwargs):
        r""" Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- samples

        .. seealso:: :func:`Distribution.rvs`
        """
        return stats.norm().rvs(m*self.dim).reshape((m,self.dim))

    def get_component(self, avars):
        r""" Return the measure :math:`\nu_{a_1}\times\cdots\times\nu_{a_k} = \mathcal{N}(0,{\bf I}_k)`

        Args:
          avars (list): list of coordinates to extract from :math:`\nu`
        """
        return StandardNormalDistribution(len(avars))

class ChainGraphGaussianDistribution(GaussianDistribution):
    def __init__(self, dim, edge_strength=.45):
        self.dim = dim
        self.edge_strength = edge_strength
        mu = np.zeros(dim)
        precision = self.omega()
        super(ChainGraphGaussianDistribution, self).__init__(mu, precision=precision)

    def omega(self):
        # create tridiagonal matrix 
        omega = np.eye(self.dim) + self.edge_strength*np.eye(self.dim,k=-1) + self.edge_strength*np.eye(self.dim,k=+1)
        # compute unnormalized sigma (covariance matrix)
        sigma_temp = np.linalg.inv(omega)
        # extract standard deviations from sigma_temp
        std_temp = np.diag(np.sqrt(np.diag(sigma_temp)))
        # scale omega by std_temp
        omega = np.dot(np.dot(std_temp, omega), std_temp)
        return omega

    def sigma(self):
        # return inverse of omega
        sigma = np.linalg.inv(self.omega)
        return sigma

    def rvs(self, m):
        # compute K, where K K^T = sigma
        K = np.linalg.cholesky(self.sigma)
        # generate 'base' samples from standard normal
        x = stats.norm().rvs(m*self.dim).reshape((m,self.dim))
        # return m realizations
        samples = np.dot(K, x.T).T
        return samples

    @property
    def nonzero_idxs(self):
        # find zero elements in omega to determine active_vars
        omegaLower = np.tril(self.omega())
        active_vars = []
        for i in range(self.dim):
            actives = np.where(omegaLower[i,:] != 0)
            active_list = list(set(actives[0]) | set([i]))
            active_list.sort(key=int)
            active_vars.append(active_list)
        return active_vars

    @property
    def graph(self):
        graph = np.zeros([self.dim,self.dim])
        graph[self.omega() != 0] = 1
        return graph

    @property
    def n_edges(self):
        return self.dim-1

class StarGraphGaussianDistribution(GaussianDistribution):
    def __init__(self, dim, edge_strength=.45):
        self.dim = dim
        self.edge_strength = edge_strength
        mu = np.zeros(dim)
        precision = self.omega()
        super(StarGraphGaussianDistribution, self).__init__(mu, precision=precision)

    def omega(self):
        # create star matrix 
        omega = np.eye(self.dim)
        omega[0,0] = self.dim
        omega[0,1:] = self.edge_strength
        omega[1:,0] = self.edge_strength
        # compute unnormalized sigma (covariance matrix)
        sigma_temp = np.linalg.inv(omega)
        # extract standard deviations from sigma_temp
        std_temp = np.diag(np.sqrt(np.diag(sigma_temp)))
        # scale omega by std_temp
        omega = np.dot(np.dot(std_temp, omega), std_temp)
        return omega

    def sigma(self):
        # return inverse of omega
        sigma = np.linalg.inv(self.omega)
        return sigma

    def rvs(self, m):
        # compute K, where K K^T = sigma
        K = np.linalg.cholesky(self.sigma)
        # generate 'base' samples from standard normal
        x = stats.norm().rvs(m*self.dim).reshape((m,self.dim))
        # return m realizations
        samples = np.dot(K, x.T).T
        return samples

    @property
    def nonzero_idxs(self):
        # find zero elements in omega to determine active_vars
        omegaLower = np.tril(self.omega())
        active_vars = []
        for i in range(self.dim):
            actives = np.where(omegaLower[i,:] != 0)
            active_list = list(set(actives[0]) | set([i]))
            active_list.sort(key=int)
            active_vars.append(active_list)
        return active_vars

    @property
    def graph(self):
        graph = np.zeros([self.dim,self.dim])
        graph[self.omega() != 0] = 1
        return graph

    @property
    def n_edges(self):
        return self.dim-1

class GridGraphGaussianDistribution(GaussianDistribution):
    def __init__(self, dim, edge_strength= 1.0):
        if (np.sqrt(dim) - int(np.sqrt(dim))) != 0:
            raise ValueError('Input dimension must be a square number')
        self.dim = dim
        self.edge_strength = edge_strength
        mu = np.zeros(dim)
        precision = self.omega()
        super(GridGraphGaussianDistribution, self).__init__(mu, precision=precision)

    def omega(self):
        dim_sq_root = int(np.sqrt(self.dim))

        # declare grid coordinates
        coords = self.zigzag(dim_sq_root)
        n_coords = len(coords)
    
        # create zero matrix
        omega = np.zeros((n_coords, n_coords))

        # pull out all coordinates
        all_coords = list(coords.values())

        # add all edges for the grid graph
        for i in range(n_coords):
            coord_val = coords[i];
            new_coords = [(coord_val[0],coord_val[1]+1), 
                          (coord_val[0],coord_val[1]-1), 
                          (coord_val[0]+1,coord_val[1]),
                          (coord_val[0]-1,coord_val[1])]
            for j in range(len(new_coords)):
                if new_coords[j] in all_coords:
                    coord_idx = all_coords.index(new_coords[j])
                    omega[i, coord_idx] = self.edge_strength
                    omega[coord_idx, i] = self.edge_strength

        # set the diagonal appropriately
        max_val = np.ceil(np.max(np.sum(np.abs(omega), axis = 0))) + 1
        omega = omega + max_val*np.eye(n_coords)
        
        # compute unnormalized sigma (covariance matrix)
        sigma_temp = np.linalg.inv(omega)
        # extract standard deviations from sigma_temp
        std_temp = np.diag(np.sqrt(np.diag(sigma_temp)))
        # scale omega by std_temp
        omega = np.dot(np.dot(std_temp, omega), std_temp)
        return omega

    def zigzag(self,n):
        # zig-zag pattern returns bijection between graph coordinates and ordering
        indexorder = sorted(((x,y) for x in range(n) for y in range(n)),
                    key = lambda p: (p[0]+p[1], -p[1] if (p[0]+p[1]) % 2 else p[1]) )
        return dict((n,index) for n,index in enumerate(indexorder))

    def sigma(self):
        # return inverse of omega
        sigma = np.linalg.inv(self.omega)
        return sigma

    def rvs(self, m):
        # compute K, where K K^T = sigma
        K = np.linalg.cholesky(self.sigma)
        # generate 'base' samples from standard normal
        x = stats.norm().rvs(m*self.dim).reshape((m,self.dim))
        # return m realizations
        samples = np.dot(K, x.T).T
        return samples

    @property
    def nonzero_idxs(self):
        #dim_sq = np.power(self.dim,2)

        # extract lower triangular matrix
        omegaLower = np.tril(self.omega())

        # add edges by...
        # variable elimination moving from highest node (dim-1) to node 2 (at most)
        for i in range(self.dim-1,1,-1):
            non_zero_ind  = np.where(omegaLower[i,:i] != 0)[0]
            if len(non_zero_ind) > 1:
                co_parents = list(itertools.combinations(non_zero_ind,2))
                for j in range(len(co_parents)):
                    row_index = max(co_parents[j])
                    col_index = min(co_parents[j])
                    omegaLower[row_index, col_index] = 1.0

        # find zero elements in chordal omega to determine active_vars
        active_vars = []
        for i in range(self.dim):
            actives = np.where(omegaLower[i,:] != 0)
            active_list = list(set(actives[0]) | set([i]))
            active_list.sort(key=int)
            active_vars.append(active_list)

        return active_vars

    @property
    def graph(self):
        graph = np.zeros([self.dim,self.dim])
        graph[self.omega() != 0] = 1
        return graph

    @property
    def n_edges(self):
        return 2.*(np.sqrt(self.dim) - 1)**2

###############################################################
# Definition of miscellaneous densities (No sampling defined) #
###############################################################
class LogNormalDistribution(FrozenDistribution_1d):
    def __init__(self, s, mu, scale):
        super(LogNormalDistribution,self).__init__()
        self.s = s
        self.mu = mu
        self.scale = scale
        self.dist = stats.lognorm(s=s,
                                  loc=mu,
                                  scale=scale)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf( x ).flatten()
    @counted
    def grad_x_pdf(self, x, *args, **kwargs):
        s = self.s
        m = self.mu
        d = self.dist
        return - d.pdf(x) * ( 1./(x-m) + np.log(x-m)/(s**2.*(x-m)) )
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf( x ).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        s = self.s
        m = self.mu
        sc = self.scale
        return - 1./(x-m) * (np.log((x-m)/sc)/s**2. + 1)
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        s = self.s
        m = self.mu
        sc = self.scale
        return (1./(x-m)**2. * ( (np.log((x-m)/sc) + s**2. - 1.)/s**2. ))[:,:,nax]

class LogisticDistribution(FrozenDistribution_1d):
    def __init__(self, mu, s):
        super(LogisticDistribution,self).__init__()
        self.mu = mu
        self.s = s
        self.dist = stats.logistic(loc=mu,scale=s)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        # Log pdf with modified asymptotic behavior
        out = np.zeros(x.shape)
        g20 = (x >= -20)
        l20 = (x < -20)
        out[g20] = self.dist.logpdf(x[g20]).flatten()
        out[l20] = (x[l20].flatten() - self.mu)/self.s
        return out.flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        mu = self.mu
        s = self.s
        out = np.zeros(x.shape)
        g20 = (x >= -20)
        l20 = (x < -20)
        g = np.exp(-(x[g20]-mu)/s)
        out[g20] = -1./s + 2./s * g/(1+g)
        out[l20] = 1./s
        return out
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        mu = self.mu
        s = self.s
        out = np.zeros(x.shape)
        g20 = (x >= -20)
        l20 = (x < -20)
        g = np.exp(-(x[g20]-mu)/s)
        out[g20] = (- 2./s**2. * g/(1+g)**2.)
        out[l20] = 0.
        return out[:,:,nax]
    # def nabla3_x_log_pdf(self, x, params=None):
    #     mu = self.mu
    #     s = self.s
    #     g = np.exp(-(x-mu)/s)
    #     return (2./s**3. * g*(1-g)/(1+g)**3.)[:,:,nax,nax]

class GammaDistribution(FrozenDistribution_1d):
    def __init__(self, kappa, theta):
        super(GammaDistribution,self).__init__()
        self.kappa = kappa
        self.theta = theta
        self.dist = stats.gamma(kappa, scale=theta)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf(x).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        k = self.kappa
        t = self.theta
        return (k-1.)/x - 1/t
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        k = self.kappa
        return ((1.-k)/x**2.)[:,:,nax]
    @counted
    def nabla3_x_log_pdf(self, x, *args, **kwargs):
        k = self.kappa
        return (2.*(k-1.)/x**3.)[:,:,nax,nax]

class BetaDistribution(FrozenDistribution_1d):
    def __init__(self, alpha, beta):
        super(BetaDistribution,self).__init__()
        self.alpha = alpha
        self.beta = beta
        self.dist = stats.beta(alpha, beta)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf(x).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        a = self.alpha
        b = self.beta
        return (a-1.)/x + (b-1.)/(x-1.)
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        a = self.alpha
        b = self.beta
        out = (1.-a)/x**2. + (1-b)/(x-1.)**2.
        return out[:,:,nax]
    @counted
    def nabla3_x_log_pdf(self, x, *args, **kwargs):
        a = self.alpha
        b = self.beta
        out = 2.*(a-1.)/x**3. + 2.*(b-1.)/(x-1.)**3.
        return out[:,:,nax,nax]

class GumbelDistribution(FrozenDistribution_1d):
    def __init__(self, mu, beta):
        super(GumbelDistribution,self).__init__()
        self.mu = mu
        self.beta = beta
        self.dist = stats.gumbel_r(loc=mu, scale=beta)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf(x).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        m = self.mu
        b = self.beta
        z = (x-m)/b
        return (np.exp(-z)-1.)/b
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        m = self.mu
        b = self.beta
        z = (x-m)/b
        return (- np.exp(-z)/b**2.)[:,:,nax]
    @counted
    def nabla3_x_log_pdf(self, x, *args, **kwargs):
        m = self.mu
        b = self.beta
        z = (x-m)/b
        return (np.exp(-z)/b**3.)[:,:,nax,nax]

class WeibullDistribution(FrozenDistribution_1d):
    def __init__(self, c, mu=0., sigma=1.):
        super(WeibullDistribution,self).__init__()
        self.c = c
        self.mu = mu
        self.sigma=sigma
        self.dist = stats.weibull_min(c=self.c, loc=self.mu, scale=self.sigma)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf(x).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        c = self.c
        m = self.mu
        s = self.sigma
        out = (c-1.)/(x-m) - c/s * ((x-m)/s)**(c-1.)
        return out
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        c = self.c
        m = self.mu
        s = self.sigma
        out = - (c-1.)/(x-m)**2. - (c*(c-1.))/s**2. * ((x-m)/s)**(c-2.)
        return out[:,:,nax]

class CauchyDistribution(FrozenDistribution_1d):
  def __init__(self, loc, scale):
    self.loc = loc
    self.scale = scale
  def pdf(self,x,params=None):
    out = stats.cauchy.pdf(x, loc = self.loc, scale = self.scale)
    return out.flatten()
  def log_pdf(self,x,params=None):
    out = stats.cauchy.logpdf(x, loc = self.loc, scale = self.scale)
    return out.flatten()
  def rvs(self,n):
    out = stats.cauchy.rvs(size=n)
    return out
  def quadrature(self,qtype,qparams):
    if qtype == 0:
      x = qparams
      l = qparams.shape[0]
      w = np.ones(l)/l
    else:
      raise NotImplementedError("Not implemented")
    return (x,w)

class StudentTDistribution(FrozenDistribution_1d):
    def __init__(self, df, mu=0., sigma=1.):
        super(StudentTDistribution,self).__init__()
        if df < 1:
            raise AttributeError("df must be >= 1")
        self.mu = mu
        self.sigma = sigma
        self.df = df
        self.dist = stats.t(df, loc=mu, scale=sigma)
    def rvs(self, n, *args, **kwargs):
        return self.dist.rvs(n).reshape((n,1))
    @counted
    def pdf(self, x, *args, **kwargs):
        return self.dist.pdf(x).flatten()
    @counted
    def log_pdf(self, x, *args, **kwargs):
        return self.dist.logpdf(x).flatten()
    @counted
    def grad_x_log_pdf(self, x, *args, **kwargs):
        m = self.mu
        s = self.sigma
        k = self.df
        return - (k+1)*(x-m)/(k*s**2 + (x-m)**2)
    @counted
    def hess_x_log_pdf(self, x, *args, **kwargs):
        m = self.mu
        s = self.sigma
        k = self.df
        out =  - (k+1)/(k*s**2 + (x-m)**2) + \
               2*(k+1)*(x-m)**2/(k*s**2 + (x-m)**2)**2
        return out[:,:,nax]
        
class BananaDistribution(PushForwardTransportMapDistribution):
    def __init__(self, a, b, mu, sigma2):
        import TransportMaps.Maps as MAPS
        gauss_map = MAPS.LinearTransportMap( mu, npla.cholesky(sigma2) )
        ban_map = MAPS.FrozenBananaMap(a, b)
        tm = MAPS.CompositeMap(ban_map, gauss_map)
        base_distribution = StandardNormalDistribution(2)
        super(BananaDistribution, self).__init__(tm, base_distribution)

class RelaxedRademacherDistribution(Distribution):
    def __init__(self, dim):
        if dim%2 != 0:
            raise ValueError("Input dimension must be an even number")
        self.dim = dim

    def rvs(self, m):
        rvs = np.zeros([m, self.dim])
        for i in range(0,self.dim,2):
            rvs[:,i] = stats.norm.rvs(size=m)
            unif = 2*stats.uniform.rvs(size=m) - 1
            rvs[:,i+1] = rvs[:,i] * unif
        return rvs

    @property
    def graph(self):
        graph = np.eye(self.dim)
        for i in range(0,self.dim,2):
            graph[i,i+1] = 1
            graph[i+1,i] = 1
        return graph

    @property
    def nonzero_idxs(self):
        # find zero elements in omega to determine active_vars
        graphLower = np.tril(self.graph())
        active_vars = []
        for i in range(self.dim):
            actives = np.where(graphLower[i,:] != 0)
            active_list = list(set(actives[0]) | set([i]))
            active_list.sort(key=int)
            active_vars.append(active_list)
        return active_vars
        
    @property
    def n_edges(self):
        return self.dim/2.

class ButterflyDistribution(Distribution):
    def __init__(self, dim):
        if dim%2 != 0:
            raise ValueError("Input dimension must be an even number")
        self.dim = dim

    def rvs(self, m):
        rvs = np.zeros([m, self.dim])
        for i in range(0,self.dim,2):
            rvs[:,i] = stats.norm.rvs(size=m)
            norm = stats.norm.rvs(size=m)
            rvs[:,i+1] = rvs[:,i] * norm
        return rvs

    @property
    def graph(self):
        graph = np.eye(self.dim)
        for i in range(0,self.dim,2):
            graph[i,i+1] = 1
            graph[i+1,i] = 1
        return graph

    @property
    def nonzero_idxs(self):
        # find zero elements in omega to determine active_vars
        graphLower = np.tril(self.graph())
        active_vars = []
        for i in range(self.dim):
            actives = np.where(graphLower[i,:] != 0)
            active_list = list(set(actives[0]) | set([i]))
            active_list.sort(key=int)
            active_vars.append(active_list)
        return active_vars
        
    @property
    def n_edges(self):
        return self.dim/2.
