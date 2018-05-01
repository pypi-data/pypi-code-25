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

import logging
import dill
import numpy as np
import numpy.linalg as npla
import scipy.linalg as scila
import scipy.optimize as sciopt

from TransportMaps.Misc import mpi_map, mpi_alloc_dmem, mpi_map_alloc_dmem, \
    counted, cached, get_sub_cache, distributed_sampling
import TransportMaps.XML as XML
from TransportMaps.Functionals.ParametricFunctionApproximationBase import \
    ParametricFunctionApproximation
from TransportMaps.Functionals.ProductDistributionParametricPullbackComponentFunctionBase \
    import ProductDistributionParametricPullbackComponentFunction
from TransportMaps.Distributions.DistributionBase import ProductDistribution
from TransportMaps.Distributions.TransportMapDistributions import \
    PullBackTransportMapDistribution, PushForwardTransportMapDistribution
from TransportMaps.Maps.MapBase import ListStackedMap
from TransportMaps.Maps.TransportMapBase import *

__all__ = ['TriangularTransportMap',
           'MonotonicTriangularTransportMap',
           'TriangularListStackedTransportMap']

nax = np.newaxis

class TriangularTransportMap(TransportMap):
    r""" Generalized triangular transport map :math:`T({\bf x},{\bf a})`.

    For :math:`{\bf x} \in \mathbb{R}^d`, and parameters
    :math:`{\bf a} \in \mathbb{R}^N`, the parametric transport map is given by

    .. math::
       :nowrap:

       T({\bf x},{\bf a}) = \begin{bmatrix}
       T_1 \left({\bf x}_1, {\bf a}^{(1)}\right) \\
       T_2 \left({\bf x}_{1:2}, {\bf a}^{(2)}\right) \\
       T_3 \left({\bf x}_{1:3}, {\bf a}^{(3)}\right) \\
       \vdots \\
       T_d \left({\bf x}_{1:d}, {\bf a}^{(d)}\right)
       \end{bmatrix}

    where :math:`{\bf a}^{(i)} \in \mathbb{R}^{n_i}` and :math:`\sum_{i=1}^d n_ = N`.

    Args:
       active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
         each dimension lists the active variables.
       approx_list (:class:`list<list>` [:math:`d`] of :class:`FunctionalApproximations.MonotonicFunctionApproximation`):
         list of monotonic functional approximations for each dimension
    """

    def __init__(self, active_vars, approx_list):
        super(TriangularTransportMap,self).__init__(active_vars, approx_list)
        # Check lower triangularity
        d0 = active_vars[0][-1]
        for i, avars in enumerate(active_vars):
            if avars[-1] != d0 + i:
                raise ValueError("The map is not generalized lower triangular.")

    def precomp_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\partial_{x_k}T_k({\bf x},{\bf a})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        for a,avar,p in zip(self.approx_list,self.active_vars,precomp['components']):
            if precomp_type == 'uni':
                a.precomp_partial_xd(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_partial_xd(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    @counted
    def det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Since the map is lower triangular,

        .. math::

           \det \nabla_{\bf x} T({\bf x}, {\bf a}) = \prod_{k=1}^d \partial_{{\bf x}_k} T_k({\bf x}_{1:k}, {\bf a}^{(k)})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return np.exp( self.log_det_grad_x(x, precomp, idxs_slice) )

    @cached([('components','dim_out')])
    @counted
    def partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`[\partial_{{\bf x}_1}T_1({\bf x}_1,{\bf a}^{(1)}),\ldots,\partial_{{\bf x}_d}T_d({\bf x}_{1:d},{\bf a}^{(d)})]`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`[\partial_{{\bf x}_1}T_1({\bf x}_1,{\bf a}^{(1)}),\ldots,\partial_{{\bf x}_d}T_d({\bf x}_{1:d},{\bf a}^{(d)})]` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluation
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0],self.dim_out))
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            out[:,k] = a.partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
        return out

    @cached([('components','dim_out')])
    @counted
    def grad_a_partial_xd(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`[\nabla_{\bf a}\partial_{{\bf x}_k} T_k]_k`

        This is

        .. math::

           \left[ \begin{array}{ccccc}
             \nabla_{{\bf a}_1}\partial_{{\bf x}_1}T_1 & 0 & \cdots & & 0 \\
             0 \nabla_{{\bf a}_2}\partial_{{\bf x}_2}T_2 & 0 & \cdots & 0 \\
             \vdots & \ddots & & & \\
             0 & & \cdots & 0 & \nabla_{{\bf a}_d}\partial_{{\bf x}_d}T_d
           \end{array} \right]
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`[\partial_{{\bf x}_1}T_1({\bf x}_1,{\bf a}^{(1)}),\ldots,\partial_{{\bf x}_d}T_d({\bf x}_{1:d},{\bf a}^{(d)})]` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim_out, self.n_coeffs))
        start = 0
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            stop = start + gapxd.shape[1]
            out[:,k,start:stop] = gapxd
            start = stop
        return out

    @cached([('components','dim_out')])
    @counted
    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Since the map is lower triangular,

        .. math::

           \log \det \nabla_{\bf x} T({\bf x}, {\bf a}) = \sum_{k=1}^d \log \partial_{{\bf x}_k} T_k({\bf x}_{1:k}, {\bf a}^{(k)})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        pxd = self.partial_xd(x, precomp=precomp, idxs_slice=idxs_slice, cache=cache)
        out = np.sum(np.log(pxd),axis=1)
        return out

    @counted
    def log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.

        Since the map is lower triangular,

        .. math::

           \log \det \nabla_{\bf y} T^{-1}({\bf x}, {\bf a}) = \sum_{k=1}^d \log \partial_{{\bf x}_k} T^{-1}_k({\bf y}_{1:k}, {\bf a}^{(k)})

        For :math:`{\bf x} = T^{-1}({\bf y}, {\bf a})`,

        .. math::

           \log \det \nabla_{\bf y} T^{-1}({\bf x}, {\bf a}) = - \sum_{k=1}^d \log \partial_{{\bf x}_k} T_k({\bf x}_{1:k}, {\bf a}^{(k)})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        return - self.log_det_grad_x( xinv )

    @cached([('components','dim_out')])
    @counted
    def grad_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\nabla_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
             :math:`\nabla_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
             at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.n_coeffs))
        start = 0
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            pxd = a.partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            # Evaluate
            stop = start + gapxd.shape[1]
            out[:,start:stop] = gapxd / pxd[:,nax]
            start = stop
        return out

    @cached([('components','dim_out')],False)
    @counted
    def hess_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
           :math:`\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_a_log_det_grad_x`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.n_coeffs, self.n_coeffs))
        start = 0
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            pxd = a.partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            # Evaluate
            stop = start + gapxd.shape[1]
            out[:,start:stop,start:stop] = \
                a.hess_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c) \
                * (1./pxd)[:,nax,nax]
            pxd2 = pxd**2.
            pxd2[pxd2<=1e-14] = 1e-14
            out[:,start:stop,start:stop] -= (gapxd[:,:,nax] * gapxd[:,nax,:]) \
                                            * (1./pxd2)[:,nax,nax]
            start = stop
        return out

    @cached([('components','dim_out')],False)
    @counted
    def action_hess_a_log_det_grad_x(self, x, da, precomp=None,
                                     idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\langle\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a}), \delta{\bf a}\rangle`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          da (:class:`ndarray<numpy.ndarray>` [:math:`N`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
           :math:`\langle\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a}), \delta{\bf a}\rangle`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_a_log_det_grad_x`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluate
        self.precomp_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.n_coeffs))
        start = 0
        for k,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            pxd = a.partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            gapxd = a.grad_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            # Evaluate
            stop = start + gapxd.shape[1]
            hapxd = a.hess_a_partial_xd(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            out[:,start:stop] = np.einsum('...ij,j->...i', hapxd, da[start:stop]) \
                                * (1./pxd)[:,nax]
            pxd2 = pxd**2.
            pxd2[pxd2<=1e-14] = 1e-14
            tmp = np.dot(gapxd, da[start:stop])
            out[:,start:stop] -= gapxd * tmp[:,nax] * (1./pxd2)[:,nax]
            start = stop
        return out

    def precomp_grad_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla_{\bf x}\partial_{x_k}T_k({\bf x},{\bf a})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        for a,avar,p in zip(self.approx_list, self.active_vars,
                            precomp['components']):
            if precomp_type == 'uni':
                a.precomp_grad_x_partial_xd(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_grad_x_partial_xd(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    @counted
    def grad_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_grad_x_partial_xd(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros((x.shape[0], self.dim))
        for k,(a,avar,p) in enumerate(zip(self.approx_list,self.active_vars,
                                          precomp['components'])):
            out[:,avar] += a.grad_x_partial_xd(x[:,avar], p) / \
                           a.partial_xd(x[:,avar], p)[:,nax]
        return out

    def precomp_hess_x_partial_xd(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla^2_{\bf x}\partial_{x_k}T_k({\bf x},{\bf a})` for :math:`k=1,\ldots,d`

        Enriches the dictionaries in the ``precomp`` list if necessary.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): list of dictionaries of precomputed values
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`dict<dict>` of :class:`list<list>` [:math:`d`]
             :class:`dict<dict>`) -- necessary structures
        """
        if precomp is None:
            precomp = {'components': [{} for i in range(self.dim)]}
        for a,avar,p in zip(self.approx_list, self.active_vars,
                            precomp['components']):
            if precomp_type == 'uni':
                a.precomp_hess_x_partial_xd(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_hess_x_partial_xd(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    @counted
    def hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_hess_x_partial_xd(x, precomp)
        out = np.zeros((x.shape[0], self.dim, self.dim))
        for k,(a,avar,p) in enumerate(zip(self.approx_list, self.active_vars,
                                          precomp['components'])):
            # 2d numpy advanced indexing
            nvar = len(avar)
            rr,cc = np.meshgrid(avar,avar)
            rr = list( rr.flatten() )
            cc = list( cc.flatten() )
            idxs = (slice(None), rr, cc)
            # Compute hess_x_partial_xd
            dxk = a.partial_xd(x[:,avar], p)
            out[idxs] += (a.hess_x_partial_xd(x[:,avar], p) / \
                          dxk[:,nax,nax]).reshape((x.shape[0],nvar**2))
            dxdxkT = a.grad_x_partial_xd(x[:,avar], p)
            dxdxkT2 = dxdxkT[:,:,nax] * dxdxkT[:,nax,:]
            out[idxs] -= (dxdxkT2 / (dxk**2.)[:,nax,nax]).reshape((x.shape[0],nvar**2))
        return out

    @counted
    def action_hess_x_log_det_grad_x(self, x, dx, precomp=None, idxs_slice=slice(None),
                                     *args, **kwargs):
        r""" Compute: :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a}), \delta{\bf x}\rangle`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`N,d`]): direction
            on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a}), \delta{\bf x}\rangle`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_hess_x_partial_xd(x, precomp)
        m = x.shape[0]
        out = np.zeros((m, self.dim))
        for k,(a,avar,p) in enumerate(zip(self.approx_list, self.active_vars,
                                          precomp['components'])):
            dxk = a.partial_xd(x[:,avar], p) # m
            out[:,avar] += np.einsum(
                '...ij,...j->...i', a.hess_x_partial_xd(x[:,avar], p), dx[:,avar] ) / \
                dxk[:,nax]
            dxdxkT = a.grad_x_partial_xd(x[:,avar], p) # m x navar
            tmp = np.einsum('ij,ij->i', dxdxkT, dx[:,avar])
            out[:,avar] -= dxdxkT * tmp[:,nax] / (dxk**2.)[:,nax]
        return out

    @counted
    def grad_a_hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                                     *args, **kwargs):
        r""" Compute: :math:`\nabla_{\bf a}\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla_{\bf a}\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_hess_x_partial_xd(x, precomp)
        out = np.zeros((x.shape[0], self.n_coeffs, self.dim, self.dim))
        start = 0
        for k,(a,avar,p) in enumerate(zip(self.approx_list, self.active_vars,
                                          precomp['components'])):

            # Compute grad_a_hess_x_sum
            dxk = a.partial_xd(x[:,avar],p)
            dadx2dxk = a.grad_a_hess_x_partial_xd(x[:,avar],p)
            dadxk    = a.grad_a_partial_xd(x[:,avar],p)
            dadxdxk  = a.grad_a_grad_x_partial_xd(x[:,avar],p)
            dx2dxk   = a.hess_x_partial_xd(x[:,avar],p)
            dxdxkT   = a.grad_x_partial_xd(x[:,avar], p)
            dxdxkT2  = dxdxkT[:,nax,:,nax] * dxdxkT[:,nax,nax,:]
            B = dadxdxk[:,:,:,nax]*dxdxkT[:,nax,nax,:]
            grad_a_hess_x_sum = (dadx2dxk / dxk[:,nax,nax,nax]) - \
                    (dx2dxk[:,nax,:,:]*dadxk[:,:,nax,nax])/(dxk**2.)[:,nax,nax,nax] - \
                    (B + B.transpose((0,1,3,2)))/(dxk**2.)[:,nax,nax,nax] + \
                    2*(dxdxkT2*dadxk[:,:,nax,nax])/(dxk**3.)[:,nax,nax,nax]

            # 2d numpy advanced indexing
            nvar = len(avar)
            stop  = start + dadxk.shape[1]
            tmp = 0
            for coeff_idx in range(start, stop):

                rr,cc = np.meshgrid(avar, avar)
                rr = list( rr.flatten() )
                cc = list( cc.flatten() )

                # Find index for coefficients and assign to out
                idxs  = (slice(None), coeff_idx, rr, cc)
                out[idxs] += grad_a_hess_x_sum[:,tmp,:,:].reshape((x.shape[0], nvar**2))
                tmp = tmp + 1

            start = stop

        return out

    @counted
    def inverse(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute: :math:`T^{-1}({\bf y},{\bf a})`

        If the map has more input than outputs :math:`d_{\rm in} > d_{\rm out}`,
        it consider the first :math:`d_{\rm in} - d_{\rm out}` values in ``x``
        to be already inverted values and feed them to the following approximations
        to find the inverse.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.


        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T^{-1}({\bf y},{\bf a})` for every evaluation point

        Raises:
          ValueError: if :math:`d_{\rm in} < d_{\rm out}`
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {}
        # Evaluation
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        xout = np.zeros(x.shape)
        skip_dim = self.dim_in - self.dim_out
        if skip_dim < 0:
            raise ValueError("The map has more output than inputs")
        xout[:,:skip_dim] = x[:,:skip_dim]
        for i in range(x.shape[0]):
            for k, (a,avar) in enumerate(zip(self.approx_list,self.active_vars)):
                xout[i,skip_dim+k] = a.inverse(xout[i,avar[:-1]], x[i,skip_dim+k])
        return xout

    @counted
    def grad_a_inverse(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`

        By the definition of the transport map :math:`T({\bf x},{\bf a})`,
        the components :math:`T_1 ({\bf x}_1, {\bf a}^{(1)})`,
        :math:`T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`, ...
        are defined by different sets of parameters :math:`{\bf a}^{(1)}`,
        :math:`{\bf a}^{(2)}`, etc.

        Differently from :func:`grad_a`,
        :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`
        is not block diagonal, but only lower block triangular
        Consequentely this function will return the full gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,N`]) --
              :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        gx = self.grad_x(xinv, precomp) # Lower triangular
        ga = self.grad_a(xinv, precomp) # List of diagonal blocks
        out = np.zeros((xinv.shape[0],self.dim,self.n_coeffs))
        rhs = np.zeros((self.dim, self.n_coeffs))
        for i in range(xinv.shape[0]):
            start = 0
            for d, gad in enumerate(ga):
                rhs[d,start:start+gad.shape[1]] = gad[i,:]
                start += gad.shape[1]
            out[i,:,:] = - scila.solve_triangular(gx[i,:,:], rhs, lower=True)
        return out

    @counted
    def grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf x} T^{-1}({\bf x},{\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           gradient matrices for every evaluation point.

        Raises:
           NotImplementedError: to be implemented in subclasses
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        gx = self.grad_x(xinv)
        gx_inv = np.zeros((xinv.shape[0], self.dim, self.dim))
        for i in range(xinv.shape[0]):
            gx_inv[i,:,:] = scila.solve_triangular(gx[i,:,:], np.eye(self.dim), lower=True)
        return gx_inv

    def precomp_minimize_kl_divergence(self, x, params, precomp_type='uni'):
        r""" Precompute necessary structures for the speed up of :func:`minimize_kl_divergence`

        Enriches the dictionaries in the ``precomp`` list if necessary.
        
        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters to be updated
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'

        Returns:
           (:class:`tuple<tuple>` (None,:class:`dict<dict>`)) -- dictionary of necessary
              strucutres. The first argument is needed for consistency with 
        """
        # Fill precomputed Vandermonde matrices etc.
        self.precomp_evaluate(x, params['params_t'], precomp_type)
        self.precomp_partial_xd(x, params['params_t'], precomp_type)

    def allocate_cache_minimize_kl_divergence(self, x):
        r""" Allocate cache space for the KL-divergence minimization

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
        """
        cache = {'tot_size': x.shape[0]}
        return (cache, )

    def reset_cache_minimize_kl_divergence(self, cache):
        r""" Reset the cache space for the KL-divergence minimization

        Args:
          cache (dict): dictionary of cached values
        """
        tot_size = cache['tot_size']
        cache.clear()
        cache['tot_size'] = tot_size

    @staticmethod
    def from_xml_element(node):
        from TransportMaps import XML_NAMESPACE
        import TransportMaps.Maps as MAPS
        # Call proper type
        t = node.attrib['type']
        dim = int(node.attrib['dim'])
        # Retrieve the active variables and the approximation list
        active_vars = [None for d in range(dim)]
        approx_list = [None for d in range(dim)]
        for comp_node in node.getchildren():
            # Figure out which component are described
            id_field = comp_node.attrib['id']
            ncomp_list = []
            if id_field == '*':
                star_comp_node = comp_node
            else:
                ncomp_list = XML.id_parser(id_field, dim)
            # Iterate over components described
            for ncomp in ncomp_list:
                if active_vars[ncomp] is not None or approx_list[ncomp] is not None:
                    raise ValueError("Component %i is multiply defined" % ncomp)
                # Get the active variables of the component
                avars_node = comp_node.find(XML_NAMESPACE + 'avars')
                avars = []
                for vars_node in avars_node.getchildren():
                    vars_field = vars_node.text
                    avars += XML.vars_parser(vars_field, ncomp)
                active_vars[ncomp] = avars
                # Construct the approximation
                approx_node = comp_node.find(XML_NAMESPACE + 'approx')
                approx = ParametricFunctionApproximation.from_xml_element(
                    approx_node, avars, totdim=ncomp+1)
                approx_list[ncomp] = approx
                
        # Init the star component
        # defining all the components which have not been defined yet
        ncomp_list = [i for i in range(dim) if active_vars[i] is None]
        for ncomp in ncomp_list:
            if active_vars[ncomp] is not None or approx_list[ncomp] is not None:
                raise ValueError("Component %i is multiply defined" % ncomp)
            # Get the active variables of the component
            avars_node = star_comp_node.find(XML_NAMESPACE + 'avars')
            avars = []
            for vars_node in avars_node.getchildren():
                vars_field = vars_node.text
                avars += XML.vars_parser(vars_field, ncomp)
            active_vars[ncomp] = avars
            # Construct the approximation
            approx_node = star_comp_node.find(XML_NAMESPACE + 'approx')
            approx = ParametricFunctionApproximation.from_xml_element(
                approx_node, avars, totdim=ncomp+1)
            approx_list[ncomp] = approx
        
        # Instantiate and return
        if t == 'intexp':
            return MAPS.IntegratedExponentialTriangularTransportMap(
                active_vars, approx_list)
        if t == 'intsq':
            return MAPS.IntegratedSquaredTriangularTransportMap(
                active_vars, approx_list)
        elif t == 'linspan':
            return MAPS.LinearSpanTriangularTransportMap(
                active_vars, approx_list)
        elif t == 'monotlinspan':
            return MAPS.MonotonicLinearSpanTriangularTransportMap(
                active_vars, approx_list)
        else:
            raise ValueError("Triangular transport map type not recognized")

class MonotonicTriangularTransportMap(TriangularTransportMap):
    r""" [Abstract] Triangular transport map which is monotone by construction.
    """    
    def get_default_init_values_minimize_kl_divergence(self):
        raise NotImplementedError("To be implemented in sub-classes")
    
    def minimize_kl_divergence(self, d1, d2,
                               qtype=None, qparams=None,
                               x=None, w=None,
                               params_d1=None, params_d2=None,
                               x0=None,
                               regularization=None,
                               tol=1e-4, maxit=100, ders=2,
                               fungrad=False, hessact=False,
                               precomp_type='uni',
                               batch_size=None,
                               mpi_pool=None,
                               grad_check=False, hess_check=False):
        r""" Compute: :math:`{\bf a}^* = \arg\min_{\bf a}\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)`

        Args:
          d1 (Distribution): distribution :math:`\pi_1`
          d2 (Distribution): distribution :math:`\pi_2`
          qtype (int): quadrature type number provided by :math:`\pi`
          qparams (object): inputs necessary to the generation of the selected
            quadrature
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
          params_d1 (dict): parameters for distribution :math:`\pi_1`
          params_d2 (dict): parameters for distribution :math:`\pi_2`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the KL-divergence problem.
          maxit (int): maximum number of iterations
          ders (int): order of derivatives available for the solution of the
            optimization problem. 0 -> derivative free, 1 -> gradient, 2 -> hessian.
          fungrad (bool): whether the target distribution provides the method
            :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
            gradient in one step. This is used only for ``ders==1``.
          hessact (bool): use the action of the Hessian. The target distribution must
            implement the function :func:`Distribution.action_hess_x_log_pdf`.
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'
          batch_size (:class:`int<int>`):
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
            If the target distribution is a :class:`ProductDistribution`, then
            the optimization problem decouples and
            ``batch_size`` is a list of lists containing the batch sizes to be
            used for each component of the map.
          mpi_pool (:class:`mpi_map.MPI_Pool` or :class:`list<list>` of ``mpi_pool``):
            pool of processes to be used, ``None`` stands for one process.
            If the target distribution is a :class:`ProductDistribution`, then
            the minimization problem decouples and ``mpi_pool`` is a list containing
            ``mpi_pool``s for each component of the map.
          grad_check (bool): whether to use finite difference to check the correctness of
            of the gradient
          hess_check (bool): whether to use finite difference to check the correctenss of
            the Hessian

        Returns:
          log (dict): log informations from the solver

        .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
          exclusive, but one pair of them is necessary.
        """
        if ders < 0:
            self.logger.warning("Value for ders too low (%d). Set to 0." % ders)
            ders = 0
        if ders > 2:
            self.logger.warning("Value for ders too high (%d). Set to 2." % ders)
            ders = 2

        def generate_quadrature(
                d1, x, w, qtype, qparams, mpi_pool):
            if (x is None) and (w is None):
                if qtype == 0: # Sample separately on the cores (lower memory)
                    (x, w) = distributed_sampling(
                        d1, 0, qparams, mpi_pool=mpi_pool)
                else:
                    (x, w) = d1.quadrature(qtype, qparams, mpi_pool=mpi_pool)
                    def alloc_quadrature(x, w):
                        return (x, w)
                    (x, w) = mpi_map_alloc_dmem(
                        alloc_quadrature,
                        scatter_tuple=(['x','w'],[x,w]),
                        dmem_key_out_list=['x', 'w'],
                        mpi_pool=mpi_pool)
            else:
                def alloc_quadrature(x, w):
                    return (x, w)
                (x, w) = mpi_map_alloc_dmem(
                    alloc_quadrature,
                    scatter_tuple=(['x','w'],[x,w]),
                    dmem_key_out_list=['x', 'w'],
                    mpi_pool=mpi_pool)
            return (x, w)

        if issubclass(type(d2.base_distribution), ProductDistribution) \
           and isinstance(d2, PullBackTransportMapDistribution):
            if batch_size is None:
                batch_size_list = [None] * self.dim
            else:
                batch_size_list = batch_size
            if mpi_pool is None:
                mpi_pool_list = [None] * self.dim
            else:
                mpi_pool_list = mpi_pool
            log_list = []
            start_coeffs = 0
            (x, w) = generate_quadrature(d1, x, w, qtype, qparams, None)
            for i, (a, avars, batch_size, mpi_pool) in enumerate(zip(
                    self.approx_list, self.active_vars, batch_size_list, mpi_pool_list)):
                f = ProductDistributionParametricPullbackComponentFunction(
                    a, d2.base_distribution.get_component([i]) )
                stop_coeffs = start_coeffs + a.n_coeffs
                sub_x0 = None if x0 is None else x0[start_coeffs:stop_coeffs]
                start_coeffs = stop_coeffs
                log = a.minimize_kl_divergence_component(
                    f, x[:,avars], w, x0=sub_x0,
                    regularization=regularization,
                    tol=tol, maxit=maxit, ders=ders,
                    fungrad=fungrad, precomp_type=precomp_type,
                    batch_size=batch_size,
                    mpi_pool=mpi_pool)
                log_list.append( log )
            return log_list
            
        else: # Not a product distribution
            (x, w) = generate_quadrature(d1, x, w, qtype, qparams, mpi_pool)
            log = self.minimize_kl_divergence_complete(
                d1, d2, x=x, w=w, params_d1=params_d1, params_d2=params_d2,
                x0=x0, regularization=regularization,
                tol=tol, maxit=maxit, ders=ders,
                fungrad=fungrad, hessact=hessact, precomp_type=precomp_type,
                batch_size=batch_size, 
                mpi_pool=mpi_pool, 
                grad_check=grad_check, hess_check=hess_check)
            return log

    def minimize_kl_divergence_complete(self, d1, d2,
                                        x=None, w=None,
                                        params_d1=None, params_d2=None,
                                        x0=None,
                                        regularization=None,
                                        tol=1e-4, maxit=100, ders=2,
                                        fungrad=False, hessact=False,
                                        precomp_type='uni',
                                        batch_size=None,
                                        mpi_pool=None,
                                        grad_check=False, hess_check=False):
        r"""
        Computes :math:`{\bf a}^* = \arg\min_{\bf a}\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)`
        for non-product distributions.

        .. seealso:: :fun:`TriangularTransportMap.minimize_kl_divergence` for a description of the parameters
        """    
        self.logger.debug("minimize_kl_divergence(): Precomputation started")

        # Distribute objects
        d2_distr = dill.loads( dill.dumps(d2) )
        d2_distr.reset_counters() # Reset counters on copy to avoid couting twice
        mpi_alloc_dmem(d2=d2_distr, mpi_pool=mpi_pool)

        # Set mpi_pool in the object
        self.mpi_pool = mpi_pool
        if batch_size is None:
            batch_size = [None] * 3
        else:
            nc = d2.transport_map.n_coeffs
            batch_size = (max(1, batch_size//nc),
                          max(1, batch_size//nc**2),
                          max(1, batch_size//nc**3))
        self.logger.debug("minimize_kl_divergence(): batch sizes: %s" % str(batch_size))

        # Link tm to d2.transport_map
        def link_tm_d2(d2):
            return (d2.transport_map,)
        (tm,) = mpi_map_alloc_dmem(
                link_tm_d2, dmem_key_in_list=['d2'], dmem_arg_in_list=['d2'],
                dmem_val_in_list=[d2], dmem_key_out_list=['tm'],
                mpi_pool=self.mpi_pool)
            
        if isinstance(d2, PullBackTransportMapDistribution):
            # Init memory
            params2 = {
                'params_pi': params_d2,
                'params_t': {'components': [{} for i in range(self.dim)]} }
            mpi_alloc_dmem(params2=params2, mpi_pool=self.mpi_pool)
            
            # precomp_minimize_kl_divergence
            bcast_tuple = (['precomp_type'],[precomp_type])
            mpi_map("precomp_minimize_kl_divergence",
                    bcast_tuple=bcast_tuple,
                    dmem_key_in_list=['params2', 'x'],
                    dmem_arg_in_list=['params', 'x'],
                    dmem_val_in_list=[params2, x],
                    obj='tm', obj_val=tm,
                    mpi_pool=self.mpi_pool, concatenate=False)
        elif isinstance(d2, PushForwardTransportMapDistribution):
            # Init memory
            params2 = { 'params_pi': params_d2,
                        'params_t': {} }
            mpi_alloc_dmem(params2=params2, mpi_pool=self.mpi_pool)
        else:
            raise AttributeError("Not recognized distribution type")
        # allocate cache
        (cache, ) = mpi_map_alloc_dmem(
            "allocate_cache_minimize_kl_divergence",
            dmem_key_in_list=['x'],
            dmem_arg_in_list=['x'],
            dmem_val_in_list=[x],
            dmem_key_out_list=['cache'],
            obj='tm', obj_val=tm,
            mpi_pool=self.mpi_pool, concatenate=False)        
        self.logger.debug("minimize_kl_divergence(): Precomputation ended")
        params = {}
        params['nobj'] = 0
        params['nda_obj'] = 0
        params['nda2_obj'] = 0
        params['nda2_obj_dot'] = 0
        params['x'] = x
        params['w'] = w
        params['d1'] = d1
        params['d2'] = d2
        params['params1'] = params_d1
        params['params2'] = params2
        params['cache'] = cache
        params['batch_size'] = batch_size
        params['regularization'] = regularization
        params['grad_check'] = grad_check
        params['hess_check'] = hess_check
        params['hess_assembled'] = False

        if x0 is None:
            x0 = self.get_default_init_values_minimize_kl_divergence()

        params['objective_cache_coeffs'] = x0 - 1.

        # Callback variables
        self.it_callback = 0
        self.ders_callback = ders
        self.params_callback = params

        # Options for optimizer
        options = {'maxiter': maxit,
                   'disp': False}

        if ders >= 1:
            if fungrad:
                fun = self.minimize_kl_divergence_tuple_grad_a_objective
                jac = True
            else:
                fun = self.minimize_kl_divergence_objective
                jac = self.minimize_kl_divergence_grad_a_objective
        
        # Solve
        if ders == 0:
            res = sciopt.minimize(
                self.minimize_kl_divergence_objective,
                args=params, x0=x0, method='BFGS', tol=tol,
                options=options, callback=self.minimize_kl_divergence_callback)
        elif ders == 1:
            res = sciopt.minimize(
                fun, args=params, x0=x0, jac=jac, method='BFGS',
                tol=tol, options=options,
                callback=self.minimize_kl_divergence_callback)
        elif ders == 2:
            if hessact:
                res = sciopt.minimize(
                    fun, args=params, x0=x0, jac=jac,
                    hessp=self.minimize_kl_divergence_action_hess_a_objective,
                    method='newton-cg', tol=tol, options=options,
                    callback=self.minimize_kl_divergence_callback)
            else:
                res = sciopt.minimize(
                    fun, args=params, x0=x0, jac=jac,
                    hessp=self.minimize_kl_divergence_action_storage_hess_a_objective,
                    method='newton-cg', tol=tol, options=options,
                    callback=self.minimize_kl_divergence_callback)

        # Clean up callback stuff
        del self.it_callback
        del self.ders_callback
        del self.params_callback

        # Get d2 from children processes and update counters
        if self.mpi_pool is not None:
            d2_child_list = self.mpi_pool.get_dmem('d2')
            d2.update_ncalls_tree( d2_child_list[0][0] )
            for (d2_child,) in d2_child_list:
                d2.update_nevals_tree(d2_child)
                d2.update_teval_tree(d2_child)

        # Log
        log = {}
        log['success'] = res['success']
        log['message'] = res['message']
        log['fval'] = res['fun']
        log['nit'] = res['nit']
        log['n_fun_ev'] = params['nobj']
        if ders >= 1:
            log['n_jac_ev'] = params['nda_obj']
            log['jac'] = res['jac']
        if ders >= 2:
            log['n_hess_ev'] = params['nda2_obj']
            
        # Attach cache to log
        if self.mpi_pool is None:
            log['cache'] = cache
        else:
            log['cache'] = self.mpi_pool.get_dmem('cache')
            
        # Display stats
        if log['success']:
            self.logger.info("minimize_kl_divergence: Optimization terminated successfully")
        else:
            self.logger.warn("minimize_kl_divergence: Minimization of KL-divergence failed.")
            self.logger.warn("minimize_kl_divergence: Message: %s" % log['message'])
        self.logger.info("minimize_kl_divergence:   Function value:          %6f" % log['fval'])
        if ders >= 1:
            self.logger.info("minimize_kl_divergence:   Norm of the Jacobian:    %6f" % npla.norm(log['jac']))
        self.logger.info("minimize_kl_divergence:   Number of iterations:    %6d" % log['nit'])
        self.logger.info("minimize_kl_divergence:   N. function evaluations: %6d" % log['n_fun_ev'])
        if ders >= 1:
            self.logger.info("minimize_kl_divergence:   N. Jacobian evaluations: %6d" % log['n_jac_ev'])
        if ders >= 2:
            self.logger.info("minimize_kl_divergence:   N. Hessian evaluations:  %6d" % log['n_hess_ev'])
            
        # Clear mpi_pool and detach object
        if self.mpi_pool is not None:
            self.mpi_pool.clear_dmem()
            self.mpi_pool = None
        
        # Set coefficients
        d2.coeffs = res['x']
        return log

class TriangularListStackedTransportMap(ListStackedMap):
    r""" Triangular transport map obtained by stacking :math:`T_1, T_2, \ldots`.

    The maps must be such that
    :math:`{\rm dim}({\rm range}(T_{i-1})) = {\rm dim}({\rm domain}(T_i))`.

    Args:
      tm_list (:class:`list` of :class:`TransportMap`): list of transport maps :math:`T_i`
    """
    def __init__(self, tm_list):
        super(TriangularListStackedTransportMap, self).__init__(tm_list)
        # Check triangularity
        dim_out = self.tm_list[0].dim_out
        for tm in self.tm_list[1:]:
            if dim_out >= tm.dim_in:
                raise ValueError("The stacked list of maps is not triangular.")
            dim_out += tm.dim_out

    def inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`T^{-1}({\bf y},{\bf a})`

        If the map has more input than outputs :math:`d_{\rm in} > d_{\rm out}`,
        it consider the first :math:`d_{\rm in} - d_{\rm out}` values in ``x``
        to be already inverted values and feed them to the following approximations
        to find the inverse.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.


        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T^{-1}({\bf y},{\bf a})` for every evaluation point

        Raises:
          ValueError: if :math:`d_{\rm in} < d_{\rm out}`
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        xinv = x.copy()
        start = 0
        for tm in self.tm_list:
            stop = start + tm.dim_out
            xinv[:,start:stop] = tm.inverse( xinv[:,:stop] )[:,start:stop]
            start = stop
        return xinv

    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Since the map is lower triangular,

        .. math::

           \log \det \nabla_{\bf x} T({\bf x}, {\bf a}) = \sum_{k=1}^d \log \partial_{{\bf x}_k} T_k({\bf x}_{1:k}, {\bf a}^{(k)})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = np.zeros(x.shape[0])
        for tm in self.tm_list:
            out += tm.log_det_grad_x( x[:,:tm.dim_in] )
        return out

    def log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        try:
            xinv = precomp['xinv']
        except (TypeError, KeyError):
            xinv = self.inverse(x, precomp)
        return - self.log_det_grad_x( xinv )
