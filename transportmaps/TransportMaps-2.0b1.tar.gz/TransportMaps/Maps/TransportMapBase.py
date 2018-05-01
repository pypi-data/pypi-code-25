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
import numpy as np
import numpy.linalg as npla
import scipy.linalg as scila

from TransportMaps.Misc import mpi_map, mpi_map_alloc_dmem, \
    SumChunkReduce, TupleSumChunkReduce, \
    cached, cached_tuple, counted, get_sub_cache, deprecate
from TransportMaps.Routines import \
    kl_divergence, grad_a_kl_divergence, hess_a_kl_divergence, \
    tuple_grad_a_kl_divergence, action_hess_a_kl_divergence, \
    storage_hess_a_kl_divergence, action_stored_hess_a_kl_divergence
import TransportMaps.FiniteDifference as FD
from TransportMaps.Distributions.DistributionBase import ProductDistribution
from TransportMaps.Functionals.ProductDistributionParametricPullbackComponentFunctionBase \
    import ProductDistributionParametricPullbackComponentFunction
from TransportMaps.Maps.MapBase import ParametricMap, \
    ListCompositeMap, CompositeMap, ListStackedMap

import copy as cp

__all__ = ['TransportMap',
           'InverseTransportMap',
           # The following are deprecated
           'CompositeTransportMap',
           'ListCompositeTransportMap',
           'ListStackedTransportMap']

nax = np.newaxis

class TransportMap(ParametricMap):
    r"""Transport map :math:`T({\bf x},{\bf a})`.

    For :math:`{\bf x} \in \mathbb{R}^d`, and parameters
    :math:`{\bf a} \in \mathbb{R}^N`, the parametric transport map is given by

    .. math::

       T({\bf x},{\bf a}) = \begin{bmatrix}
       T_1 \left({\bf x}, {\bf a}^{(1)}\right) \\
       T_2 \left({\bf x}, {\bf a}^{(2)}\right) \\
       T_3 \left({\bf x}, {\bf a}^{(3)}\right) \\
       \vdots \\
       T_d \left({\bf x}, {\bf a}^{(d)}\right)
       \end{bmatrix}

    where :math:`{\bf a}^{(i)} \in \mathbb{R}^{n_i}` and :math:`\sum_{i=1}^d n_i = N`.

    Args:
       active_vars (:class:`list<list>` [:math:`d`] of :class:`list<list>`): for
         each dimension lists the active variables.
       approx_list (:class:`list<list>` [:math:`d`] of :class:`FunctionalApproximations.MonotonicFunctionApproximation`):
         list of monotonic functional approximations for each dimension
    """    
    def __init__(self, active_vars, approx_list):
        if len(active_vars) != len(approx_list):
            raise ValueError("Inconsistent dimensions")
        for i,(vs,approx) in enumerate(zip(active_vars,approx_list)):
            if len(vs) != approx.dim:
                raise ValueError("The dimension of the %d-th approximation " % i +
                                 "is inconsistent")
        dim_in = max([ max(avars) for avars in active_vars ]) + 1
        dim_out = len(active_vars)
        super(TransportMap, self).__init__(dim_in, dim_out)
        self.approx_list = approx_list
        self.active_vars = active_vars
        self.mpi_pool = None

    def get_ncalls_tree(self, indent=""):
        out = super(TransportMap, self).get_ncalls_tree(indent)
        for i, a in enumerate(self.approx_list):
            out += a.get_ncalls_tree(indent + " T%d - " % i)
        return out

    def get_nevals_tree(self, indent=""):
        out = super(TransportMap, self).get_nevals_tree(indent)
        for i, a in enumerate(self.approx_list):
            out += a.get_nevals_tree(indent + " T%d - " % i)
        return out

    def get_teval_tree(self, indent=""):
        out = super(TransportMap, self).get_teval_tree(indent)
        for i, a in enumerate(self.approx_list):
            out += a.get_teval_tree(indent + " T%d - " % i)
        return out

    def update_ncalls_tree(self, obj):
        super(TransportMap, self).update_ncalls_tree( obj )
        for a, obj_a in zip(self.approx_list, obj.approx_list):
            a.update_ncalls_tree( obj_a )

    def update_nevals_tree(self, obj):
        super(TransportMap, self).update_nevals_tree( obj )
        for a, obj_a in zip(self.approx_list, obj.approx_list):
            a.update_nevals_tree( obj_a )

    def update_teval_tree(self, obj):
        super(TransportMap, self).update_teval_tree( obj )
        for a, obj_a in zip(self.approx_list, obj.approx_list):
            a.update_teval_tree( obj_a )

    def reset_counters(self):
        super(TransportMap, self).reset_counters()
        for a in self.approx_list:
            a.reset_counters()
        
    @property
    def n_coeffs(self):
        r""" Returns the total number of coefficients.

        Returns:
           total number :math:`N` of coefficients characterizing the transport map.
        """
        return np.sum([ a.n_coeffs for a in self.approx_list ])

    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.
        """
        out = np.zeros( self.n_coeffs )
        start = 0
        for a in self.approx_list:
            n_coeffs = np.sum( a.n_coeffs )
            out[start:start+n_coeffs] = a.coeffs
            start += n_coeffs
        return out

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps

        Raises:
           ValueError: if the number of input coefficients does not match the
              number of required coefficients :func:`n_coeffs`.
        """
        start = 0
        for a in self.approx_list:
            n_coeffs = a.n_coeffs
            a.coeffs = coeffs[start:start+n_coeffs]
            start += n_coeffs

    def get_identity_coeffs(self):
        r""" [Abstract] Returns the coefficients corresponding to the identity map

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients

        Raises:
          NotImplementedError: must be implemented in subclasses.
        """
        raise NotImplementedError("Must be implemented in subclasses.")

    def precomp_evaluate(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`T({\bf x},{\bf a})`

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
            precomp = {'components': [{} for i in range(self.dim_out)]}
        for a,avar,p in zip(self.approx_list, self.active_vars, precomp['components']):
            if precomp_type == 'uni':
                a.precomp_evaluate(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_evaluate(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    @cached([('components','dim_out')])
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate the transport map at the points :math:`{\bf x} \in \mathbb{R}^{m \times d}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dict<dict>`): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- transformed points

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluation
        self.precomp_evaluate(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        xout = np.zeros((x.shape[0], self.dim_out))
        for i,(a,avar,p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            xout[:,i] = a.evaluate( x[:,avar], p,
                                    idxs_slice=idxs_slice, cache=c )
        return xout

    def __call__(self, x):
        r"""
        Calls :func:`evaluate`.
        """
        return self.evaluate( x )

    @counted
    def inverse(self, y, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Compute: :math:`T^{-1}({\bf y},{\bf a})`

        Args:
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (dict): precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T^{-1}({\bf y},{\bf a})` for every evaluation point
        """
        raise NotImplementedError("Abstract method.")

    @cached([('components','dim_out')],False)
    @counted
    def grad_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\nabla_{\bf a} T({\bf x},{\bf a})`

        By the definition of the transport map :math:`T({\bf x},{\bf a})`,
        the components :math:`T_1 ({\bf x}_1, {\bf a}^{(1)})`,
        :math:`T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`, ...
        are defined by different sets of parameters :math:`{\bf a}^{(1)}`,
        :math:`{\bf a}^{(2)}`, etc.

        For this reason :math:`\nabla_{\bf a} T({\bf x},{\bf a})`
        is block diagonal:

        .. math::
           :nowrap:

           \nabla_a T({\bf x},{\bf a}) = \begin{bmatrix}
           \left[ \nabla_{{\bf a}^{(1)}} T_1 ({\bf x}_1, {\bf a}^{(1)}) \right]^T & {\bf 0} & \cdots \\
           {\bf 0} & \left[ \nabla_{{\bf a}^{(2)}} T_2 ({\bf x}_{1:2}, {\bf a}^{(2)}) \right]^T & \\
           \vdots & & \ddots
           \end{bmatrix}

        Consequentely this function will return only the diagonal blocks of the gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (:class:`dics<dict>`): cache
          
        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i`]) --
              list containing
              :math:`\nabla_{{\bf a}^{(1)}} T_1 ({\bf x}_1, {\bf a}^{(1)})`,
              :math:`\nabla_{{\bf a}^{(2)}} T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`,
              etc.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluation
        self.precomp_evaluate(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = []
        for k,(a,avar,p,c) in enumerate(zip(self.approx_list,self.active_vars,
                                          precomp['components'], comp_cache)):
            ga = a.grad_a(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            out.append( ga )
        return out

    @counted
    def grad_a_inverse(self, x, precomp=None, idxs_slice=slice(None)):
        r""" [Abstract] Compute :math:`\nabla_{\bf a} T^{-1}({\bf x},{\bf a})`

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
        raise NotImplementedError("Abstract method")

    @cached([('components','dim_out')],False)
    @counted
    def hess_a(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\nabla^2_{\bf a} T({\bf x},{\bf a})`.

        As in the case of :func:`grad_a`, the :math:`d \times N \times N`
        Hessian of T({\bf x},{\bf a}) is (hyper) block diagonal.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i,n_i`]) --
              list containing
              :math:`\nabla^2_{{\bf a}^{(1)}} T_1 ({\bf x}_1, {\bf a}^{(1)})`,
              :math:`\nabla^2_{{\bf a}^{(2)}} T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`,
              etc.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        # Evaluation
        self.precomp_evaluate(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return [ a.hess_a(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
                 for k,(a,avar,p,c)
                 in enumerate(zip(self.approx_list,self.active_vars,
                                  precomp['components'], comp_cache)) ]

    @cached([('components','dim_out')],False)
    @counted
    def action_hess_a(self, x, da, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\langle\nabla^2_{\bf a} T({\bf x},{\bf a}), \delta{\bf a}\rangle`.

        As in the case of :func:`grad_a`, the :math:`d \times N `
        actions of the Hessian of T({\bf x},{\bf a}) is (hyper) block diagonal.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          da (:class:`ndarray<numpy.ndarray>` [:math:`N`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i,n_i`]) --
              list containing
              :math:`\langle\nabla^2_{{\bf a}^{(1)}} T_1 ({\bf x}_1, {\bf a}^{(1)}),\delta{\bf a}^{(1)}\rangle`,
              :math:`\langle\nabla^2_{{\bf a}^{(2)}} T_2 ({\bf x}_{1:2}, {\bf a}^{(2)}),\delta{\bf a}^{(2)}\rangle`,
              etc.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_evaluate(x, precomp)
        # Init sub-cache if necessary
        comp_cache = get_sub_cache(cache, ('components',self.dim_out))
        out = []
        start = 0
        for k, (a, avar, p, c) in enumerate(zip(self.approx_list,self.active_vars,
                                             precomp['components'], comp_cache)):
            stop = start + a.n_coeffs
            ha = a.hess_a(x[:,avar], p, idxs_slice=idxs_slice, cache=c)
            out.append( np.einsum('...ij,j->...i', ha, da[start:stop]) )
            start = stop
        return out

    @cached([('components','dim_out')],False)
    @counted
    def grad_a_grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a} \nabla_{\bf x} T({\bf x},{\bf a})`

        By the definition of the transport map :math:`T({\bf x},{\bf a})`,
        the components :math:`T_1 ({\bf x}_1, {\bf a}^{(1)})`,
        :math:`T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`, ...
        are defined by different sets of parameters :math:`{\bf a}^{(1)}`,
        :math:`{\bf a}^{(2)}`, etc.

        For this reason :math:`\nabla_{\bf a} \nabla_{\bf x} T({\bf x},{\bf a})`
        is block diagonal:

        .. math::
           :nowrap:

           \nabla_a \nabla_{\bf x} T({\bf x},{\bf a}) = \begin{bmatrix}
           \left[ \nabla_{{\bf a}^{(1)}} \nabla_{\bf x}_1 T_1 ({\bf x}_1, {\bf a}^{(1)}) \right]^T & {\bf 0} & \cdots \\
           {\bf 0} & \left[ \nabla_{{\bf a}^{(2)}} \nabla_{\bf x}_{1:2} T_2 ({\bf x}_{1:2}, {\bf a}^{(2)}) \right]^T & \\
           \vdots & & \ddots
           \end{bmatrix}

        Consequentely this function will return only the diagonal blocks of the gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i`]) --
              list containing
              :math:`\nabla_{{\bf a}^{(1)}} \nabla_{\bf x}_1 T_1 ({\bf x}_1, {\bf a}^{(1)})`,
              :math:`\nabla_{{\bf a}^{(2)}} \nabla_{\bf x}_{1:2} T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`,
              etc.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_evaluate(x, precomp)
        self.precomp_grad_x(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = []
        for k,(a,avar,p) in enumerate(zip(self.approx_list,self.active_vars,
                                          precomp['components'])):
            ga = a.grad_a_grad_x(x[:,avar], p, idxs_slice=idxs_slice)
            out.append( ga )
        return out

    def precomp_grad_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla_{\bf x}T({\bf x},{\bf a})`

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
            precomp = {'components': [{} for i in range(self.dim_out)]}
        for a,avar,p in zip(self.approx_list, self.active_vars,
                            precomp['components']):
            if precomp_type == 'uni':
                a.precomp_grad_x(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_grad_x(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    @cached([('components','dim_out')])
    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf x} T({\bf x},{\bf a})`.

        This is
        
        .. math::
            :nowrap:

            \nabla_{\bf x} T({\bf x},{\bf a}) =
                 \begin{bmatrix}
                 \nabla_{\bf x}  T_1({\bf x},{\bf a})  \\
                 \nabla_{\bf x}  T_2({\bf x},{\bf a})  \\
                 \vdots \\
                 \nabla_{\bf x}  T_d({\bf x},{\bf a})
                 \end{bmatrix}

        for every evaluation point.

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
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_grad_x(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim_out, self.dim_in) )
        for k,(a,avar,p) in enumerate(zip(self.approx_list, self.active_vars,
                                          precomp['components'])):
            out[:,k,avar] = a.grad_x(x[:,avar], p, idxs_slice=idxs_slice)
        return out

    def precomp_hess_x(self, x, precomp=None, precomp_type='uni'):
        r""" Precompute necessary structures for the evaluation of :math:`\nabla^2_{\bf x}T({\bf x},{\bf a})`

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
            precomp = {'components': [{} for i in range(self.dim_out)]}
        for a,avar,p in zip(self.approx_list, self.active_vars,
                            precomp['components']):
            if precomp_type == 'uni':
                a.precomp_hess_x(x[:,avar], p)
            elif precomp_type == 'multi':
                a.precomp_Vandermonde_hess_x(x[:,avar], p)
            else: raise ValueError("Unrecognized precomp_type")
        return precomp

    @cached([('components','dim_out')],False)
    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla^2_{\bf x} T({\bf x},{\bf a})`.

        This is the tensor

        .. math::

           \left[\nabla^2_{\bf x} T({\bf x},{\bf a})\right]_{i,k,:,:} = \nabla^2_{\bf x} T_k({\bf x}^{(i)},{\bf a}^{(k)})

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_hess_x(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim_out, self.dim_in, self.dim_in) )
        for k,(a,avar,p) in enumerate(zip(self.approx_list,
                                          self.active_vars,
                                          precomp['components'])):
            # 2d numpy advanced indexing
            nvar = len(avar)
            rr,cc = np.meshgrid(avar,avar)
            rr = list( rr.flatten() )
            cc = list( cc.flatten() )
            idxs = (slice(None), k, rr, cc)
            # Compute hess_x
            out[idxs] = a.hess_x(x[:,avar], p, idxs_slice=idxs_slice).reshape((x.shape[0],nvar**2))
        return out

    @cached([('components','dim_out')],False)
    @counted
    def action_hess_x(self, x, dx, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\langle\nabla^2_{\bf x} T({\bf x},{\bf a}),\delta{\bf x}\rangle`.

        This is the tensor

        .. math::

           \left[\nabla^2_{\bf x} T({\bf x},{\bf a})\right]_{i,k,:i} = \langle \nabla^2_{\bf x} T_k({\bf x}^{(i)},{\bf a}^{(k)}), \delta{\bf x}\rangle

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim_out)]}
        self.precomp_hess_x(x, precomp)
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        out = np.zeros( (x.shape[0], self.dim_out, self.dim_in) )
        for k,(a,avar,p) in enumerate(zip(self.approx_list,
                                          self.active_vars,
                                          precomp['components'])):
            # 2d numpy advanced indexing
            nvar = len(avar)
            idxs = (slice(None), k, avar)
            # Compute hess_x
            hxTk = a.hess_x(x[:,avar], p, idxs_slice=idxs_slice)
            out[idxs] = np.einsum('...ij,...j->...i', hxTk, dx[:,avar])
        return out

    @cached([('components','dim_out')],False)
    @counted
    def grad_a_hess_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a} \nabla^2_{\bf x} T({\bf x},{\bf a})`.

        By the definition of the transport map :math:`T({\bf x},{\bf a})`,
        the components :math:`T_1 ({\bf x}_1, {\bf a}^{(1)})`,
        :math:`T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`, ...
        are defined by different sets of parameters :math:`{\bf a}^{(1)}`,
        :math:`{\bf a}^{(2)}`, etc.

        For this reason :math:`\nabla_{\bf a} \nabla^2_{\bf x} T({\bf x},{\bf a})`
        is block diagonal:

        .. math::
           :nowrap:

           \nabla_a \nabla^2_{\bf x} T({\bf x},{\bf a}) = \begin{bmatrix}
           \left[ \nabla_{{\bf a}^{(1)}} \nabla^2_{\bf x}_1 T_1 ({\bf x}_1, {\bf a}^{(1)}) \right]^T & {\bf 0} & \cdots \\
           {\bf 0} & \left[ \nabla_{{\bf a}^{(2)}} \nabla^2_{\bf x}_{1:2} T_2 ({\bf x}_{1:2}, {\bf a}^{(2)}) \right]^T & \\
           \vdots & & \ddots
           \end{bmatrix}

        Consequentely this function will return only the diagonal blocks of the hessian.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i`]) --
              list containing
              :math:`\nabla_{{\bf a}^{(1)}} \nabla^2_{\bf x}_1 T_1 ({\bf x}_1, {\bf a}^{(1)})`,
              :math:`\nabla_{{\bf a}^{(2)}} \nabla^2_{\bf x}_{1:2} T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`,
              etc.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """

        if precomp is None:
            idxs_slice = slice(None)
            precomp = {'components': [{} for i in range(self.dim)]}
        self.precomp_hess_x(x, precomp)
        if x.shape[1] != self.dim:
            raise ValueError("dimension mismatch")
        out = []
        for k,(a,avar,p) in enumerate(zip(self.approx_list,self.active_vars,
                                          precomp['components'])):
            ga = a.grad_a_hess_x(x[:,avar], p, idxs_slice=idxs_slice)
            out.append( ga )
        return out

    def grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" [Abstract] Compute :math:`\nabla_{\bf x} T^{-1}({\bf x},{\bf a})`.

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
        raise NotImplementedError("To be implemented in subclasses")

    @counted
    def det_grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" [Abstract] Compute: :math:`\det \nabla_{\bf x} T({\bf x}, {\bf a})`.

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
        """
        return np.exp(self.log_det_grad_x(
            x, precomp, idxs_slice=idxs_slice, *args, **kwargs))

    @cached()
    @counted
    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" [Abstract] Compute: :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

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
        """
        raise NotImplementedError("Abstract method")

    @counted
    def log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None),
                               *args, **kwargs):
        r""" [Abstract] Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})` at every
           evaluation point
        """
        raise NotImplementedError("Abstract method")

    @cached()
    @counted
    def grad_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
             :math:`\nabla_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
             at every evaluation point

        .. seealso:: :func:`log_det_grad_x`
        """
        raise NotImplementedError("Abstract method")

    @cached()
    @counted
    def hess_a_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
           :math:`\nabla^2_{\bf a} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_a_log_det_grad_x`
        """
        raise NotImplementedError("Abstract method")

    @cached()
    @counted
    def grad_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

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

        .. seealso:: :func:`log_det_grad_x`.
        """
        raise NotImplementedError("Abstract method")

    @cached()
    @counted
    def hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None),
                              *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

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

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        raise NotImplementedError("Abstract method")

    def grad_x_log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None),
                                      *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`
           at every evaluation point

        .. seealso:: :func:`log_det_grad_x`.
        """
        raise NotImplementedError("Abstract method")

    def hess_x_log_det_grad_x_inverse(self, x, precomp=None, idxs_slice=slice(None),
                                      *args, **kwargs):
        r""" [Abstract] Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`
           at every evaluation point

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        raise NotImplementedError("Abstract method")

    def _evaluate_grad_a_log_pullback(self, gxlpdf, ga_list, galdgx):
        out = np.zeros((gxlpdf.shape[0],self.n_coeffs))
        start = 0
        for k,grad in enumerate(ga_list):
            stop = start + grad.shape[1]
            out[:,start:stop] = gxlpdf[:,k,nax] * grad
            start = stop
        out += galdgx
        return out
        
    @cached([('pi',None),('t',None)])
    @counted
    def grad_a_log_pullback(self, x, pi, params_t=None, params_pi=None,
                            idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\nabla_{\bf a}[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert ]`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          pi (:class:`Distributions.Distribution`): distribution to be pulled back       
          params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
          params_pi (dict): parameters for the evaluation of :math:`\pi`
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
           :math:`\nabla_{\bf a}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right]`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_a`, :func:`grad_a_log_det_grad_x`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        # Init sub-cache if necessary
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        ev = self.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        ga_list = self.grad_a(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        gxlpdf = pi.grad_x_log_pdf(
            ev, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)
        galdgx = self.grad_a_log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        return self._evaluate_grad_a_log_pullback(gxlpdf, ga_list, galdgx)

    @cached_tuple(['log_pullback', 'grad_a_log_pullback'],[('pi',None),('t',None)])
    @counted
    def tuple_grad_a_log_pullback(self, x, pi, params_t=None, params_pi=None,
                                  idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\left(\log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a}),\nabla_{\bf a}[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert ]\right)`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          pi (:class:`Distributions.Distribution`): distribution to be pulled back        
          params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
          params_pi (dict): parameters for the evaluation of :math:`\pi`
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
           (:class:`tuple`) --
            :math:`\left(\log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a}),\nabla_{\bf a}[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert ]\right)`

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_a`, :func:`grad_a_log_det_grad_x`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        # Init sub-cache if necessary
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        ev = self.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        ldgx = self.log_det_grad_x(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        ga_list = self.grad_a(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        galdgx = self.grad_a_log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        lpdf, gxlpdf = pi.tuple_grad_x_log_pdf(
            ev, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)
        return ( self._evaluate_log_transport(lpdf, ldgx),
                 self._evaluate_grad_a_log_pullback(gxlpdf, ga_list, galdgx) )

    @cached([('pi',None),('t',None)], False)
    @counted
    def hess_a_log_pullback(self, x, pi, params_t=None, params_pi=None,
                            idxs_slice=slice(None), cache=None ):
        r""" Compute :math:`\nabla^2_{\bf a}[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert ]`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          pi (:class:`Distributions.Distribution`): distribution to be pulled back        
          params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
          params_pi (dict): parameters for the evaluation of :math:`\pi`
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
           :math:`\nabla^2_{\bf a}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right]`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_a`, :func:`hess_a`, :func:`grad_x_log_pullback`, :func:`hess_x_log_pullback`, :func:`hess_a_log_det_grad_x`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        if issubclass(type(pi), ProductDistribution):
            n = x.shape[0]
            hess_a_sum = np.zeros((n,self.n_coeffs,self.n_coeffs))
            # currently not using parallel implementation (batch_size_list, mpi_pool_list)
            # currently using params_t and params_pi assuming None
            start_j = 0
            for i,(a,avars) in enumerate(zip(self.approx_list,self.active_vars)):
                pi_i = pi.get_component([i])
                pS_i = ProductDistributionParametricPullbackComponentFunction(a, pi_i)
                stop_j = start_j + a.n_coeffs
                hess_a_sum[np.ix_(range(n), range(start_j,stop_j), range(start_j,stop_j))] += pS_i.hess_a(x[:,avars])
                start_j = stop_j
            return hess_a_sum
        else:
            # Init sub-cache if necessary
            pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
       	    xval = self.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
            grad_list = self.grad_a(x, precomp=params_t, idxs_slice=idxs_slice,
                                cache=t_cache) # List of d (n x m) arrays
            hess_list = self.hess_a(x, precomp=params_t, idxs_slice=idxs_slice,
                                cache=t_cache) # List of d (n x m x m) arrays
            dxlogpull = pi.grad_x_log_pdf(
                xval, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache) # (n x d) array
            dx2logpull = pi.hess_x_log_pdf(
                xval, params=params_pi,
                idxs_slice=idxs_slice, cache=pi_cache) # (n x d x d) array
            out = np.empty((x.shape[0],self.n_coeffs,
                           self.n_coeffs)) # Initialized by first addend
            # First addend
            start_j = 0
            for j in range(self.dim_out):
                g = grad_list[j]
                stop_j = start_j + g.shape[1]
                start_k = 0
                for k in range(self.dim_out):
                    h = grad_list[k]
                    stop_k = start_k + h.shape[1]
                    tmp = dx2logpull[:,j,k,nax] * g
                    out[:,start_j:stop_j,start_k:stop_k] = tmp[:,:,nax] * h[:,nax,:]
                    start_k = stop_k
                start_j = stop_j
            # Second addend
            start = 0
            for k,hess in enumerate(hess_list):
                stop = start + hess.shape[1]
                out[:,start:stop,start:stop] += dxlogpull[:,k,nax,nax] * hess
                start = stop
            # Add Hessian of the log determinant term
            out += self.hess_a_log_det_grad_x(x, precomp=params_t,
                                          idxs_slice=idxs_slice, cache=t_cache)
            return out

    def grad_a_hess_x_log_pullback(self, pi, x, params_t=None, params_pi=None,
                            idxs_slice=slice(None) ):
        r""" Compute :math:`\nabla_{\bf a} \nabla^2_{\bf x}[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert ]`.

        Args:
          pi (:class:`Distributions.Distribution`): distribution to be pulled back
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
          params_pi (dict): parameters for the evaluation of :math:`\pi`
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N,d,d`]) --
           :math:`\nabla_{\bf a} \nabla^2_{\bf x}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right]`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_a`, :func:`hess_a`, :func:`grad_x_log_pullback`, :func:`hess_x_log_pullback`, :func:`hess_a_log_det_grad_x`.
        """

        if issubclass(type(pi), ProductDistribution):
            n = x.shape[0]
            grad_a_hess_x_sum = np.zeros((n,self.n_coeffs,self.dim,self.dim))
            # currently not using parallel implementation (batch_size_list, mpi_pool_list)
            # currently using params_t and params_pi assuming None
            start_j = 0
            for i,(a,avars) in enumerate(zip(self.approx_list,self.active_vars)):
                pi_i = pi.get_component([i])
                pS_i = ProductDistributionParametricPullbackComponentFunction(a, pi_i)
                stop_j = start_j + a.n_coeffs
                grad_a_hess_x_sum[np.ix_(range(n), range(start_j,stop_j), avars, avars)] += pS_i.grad_a_hess_x(x[:,avars])
                start_j = stop_j
            return grad_a_hess_x_sum
        else:
            print('not implemented yet')

    @cached([('pi',None),('t',None)], False)
    @counted
    def action_hess_a_log_pullback(
            self, x, pi, da, params_t=None, params_pi=None, idxs_slice=slice(None),
            cache=None):
        r""" Compute :math:`\langle\nabla^2_{\bf a}[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert ], \delta{\bf a}\rangle`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          pi (:class:`Distributions.Distribution`): distribution to be pulled back       
          da (:class:`ndarray<numpy.ndarray>` [:math:`N`]): direction
            on which to evaluate the Hessian
          params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
          params_pi (dict): parameters for the evaluation of :math:`\pi`
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          cache (dict): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N,N`]) --
           :math:`\langle\nabla^2_{\bf a}[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert ], \delta{\bf x}\rangle`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_a`, :func:`hess_a`, :func:`grad_x_log_pullback`, :func:`hess_x_log_pullback`, :func:`hess_a_log_det_grad_x`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        # Init sub-cache if necessary
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        m = x.shape[0]
        xval = self.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)

        # First addend
        grad_list = self.grad_a(x, precomp=params_t, idxs_slice=idxs_slice,
                                cache=t_cache) # List of d (m x n) arrays
        dx = np.zeros((m, self.dim_out))
        start = 0
        for j, g in enumerate(grad_list):
            stop = start + g.shape[1]
            dx[:,j] = np.dot(g, da[start:stop])
            start = stop
        ahxlpdf = pi.action_hess_x_log_pdf(
            xval, dx, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache) # m x d
        A = np.zeros((m, self.n_coeffs)) # m x N
        start = 0
        for j, g in enumerate(grad_list):
            stop = start + g.shape[1]
            A[:,start:stop] = g * ahxlpdf[:,[j]]
            start = stop

        # Second addend
        action_hess_list = self.action_hess_a(
            x, da, precomp=params_t, idxs_slice=idxs_slice,
            cache=t_cache) # list d (m x n)
        dxlogpull = pi.grad_x_log_pdf(
            xval, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache) # (m x d) array
        B = np.zeros((m, self.n_coeffs))
        start = 0
        for j, ah in enumerate(action_hess_list):
            stop = start + ah.shape[1]
            B[:,start:stop] = dxlogpull[:,[j]] * ah
            start = stop
        
        # Add Hessian of the log determinant term
        C = self.action_hess_a_log_det_grad_x(
            x, da, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        return A + B + C

    @counted
    def grad_a_log_pushforward(self, x, pi, params_t=None, params_pi=None,
                               idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \det \nabla_{\bf x}T^{-1}({\bf x,a}) \right]` .

        For :math:`{\bf z} = T^{-1}({\bf x,a})`,

        .. math::
        
           \nabla_{\bf a}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \det \nabla_{\bf x}T^{-1}({\bf x,a}) \right] &= \nabla_{\bf a} T({\bf z, a})^\top \nabla_{\bf x} T({\bf z,a})^{-\top} \left( \sum_{i=1}^d \frac{\nabla_{\bf x}\partial_{x_i}T_i({\bf z}_{1:i},{\bf a}_i)}{\partial_{x_i}T_i({\bf z}_{1:i},{\bf a}_i)} - \nabla_{\bf x}\log\pi \right) \\
           & - \sum_{i=1}^d \frac{\nabla_{\bf a}\partial_{x_i}T_i({\bf z}_{1:i},{\bf a}_i)}{\partial_{x_i}T_i({\bf z}_{1:i},{\bf a}_i)}
           

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          pi (:class:`Distributions.Distribution`): distribution to be pulled back        
          params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
          params_pi (dict): parameters for the evaluation of :math:`\pi`
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,N`]) --
           :math:`\nabla_{\bf a}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \vert\det \nabla_{\bf x}T^{-1}({\bf x,a})\vert \right]`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_a_inverse`, :func:`grad_a_log_det_grad_x_inverse`.
        """
        xinv = self.inverse(x, params_t, idxs_slice=idxs_slice)
        gx = self.grad_x(xinv) # Lower triangular
        ga_list = self.grad_a(xinv) # List of diagonal blocks
        out = np.zeros( (x.shape[0], self.n_coeffs) )
        # Solve linear system
        tmp = self.grad_x_log_det_grad_x(xinv)
        tmp -= pi.grad_x_log_pdf(xinv)
        for i in range(x.shape[0]):
            scila.solve_triangular(gx[i,:,:], tmp[i,:],
                                   lower=True, trans='T', overwrite_b=True)
        # Finish computing first term
        start = 0
        for d, ga in enumerate(ga_list):
            stop = start + ga.shape[1]
            out[:,start:stop] = ga * tmp[:,d,nax]
            start += ga.shape[1]
        # Add second term
        out -= self.grad_a_log_det_grad_x(xinv)
        return out

    def minimize_kl_divergence(self, d1, d2,
                               qtype=None, qparams=None,
                               x=None, w=None,
                               params1=None, params2=None,
                               x0=None,
                               regularization=None,
                               tol=1e-4, maxit=100, ders=2,
                               fungrad=False,
                               precomp_type='uni',
                               batch_size=None,
                               nprocs=None,
                               grad_check=False, hess_check=False):
        r""" [Abstract] Compute: :math:`{\bf a}^* = \arg\min_{\bf a}\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)`

        Args:
          d1 (Distribution): distribution :math:`\pi_1`
          d2 (Distribution): distribution :math:`\pi_2`
          qtype (int): quadrature type number provided by :math:`\pi`
          qparams (object): inputs necessary to the generation of the selected
            quadrature
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
          params1 (dict): parameters for distribution :math:`\pi_1`
          params2 (dict): parameters for distribution :math:`\pi_2`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the KL-divergence problem.
          maxit (int): maximum number of iterations
          ders (int): order of derivatives available for the solution of the
            optimization problem.
            0 -> derivative free,
            1 -> gradient,
            2 -> hessian.
          fungrad (bool): whether the distributions :math:`\pi_1,\pi_2` provide the method
            :func:`Distribution.tuple_grad_x_log_pdf` computing the evaluation and the
            gradient in one step. This is used only for ``ders==1``.
          precomp_type (str): whether to precompute univariate Vandermonde matrices 'uni' or
            multivariate Vandermonde matrices 'multi'
          batch_size (:class:`list<list>` [3 or 2] of :class:`int<int>`): the list contains the
            size of the batch to be used for each iteration. A size ``1`` correspond
            to a completely non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one.
          nprocs (int): number of processors to be used for function evaluation,
            gradient evaluation and Hessian evaluation. Value ``None`` will determine the
            MPI size automatically (or set to ``nprocs=1`` if MPI is not supported)
          grad_check (bool): whether to use finite difference to check the correctness of
            of the gradient
          hess_check (bool): whether to use finite difference to check the correctenss of
            the Hessian

        Returns:
          log (dict): log informations from the solver

        .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
          exclusive, but one pair of them is necessary.
        """
        raise NotImplementedError("Abstract method.")

    def minimize_kl_divergence_objective(self, a, params):
        r""" Objective function :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` for the KL-divergence minimization.

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          params (dict): dictionary of parameters
        """
        params['nobj'] += 1
        x = params['x']
        w = params['w']
        d1 = params['d1']
        d2 = params['d2']
        params1 = params['params1']
        params2 = params['params2']
        cache = params['cache']
        batch_size = params['batch_size']
        # Update distribution coefficients
        d2.coeffs = a
        bcast_tuple = (['coeffs'],[a])
        mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
                obj='d2', obj_val=d2,
                mpi_pool=self.mpi_pool, concatenate=False)
        # Reset cache
        if (params['objective_cache_coeffs'] != self.coeffs).any():
            params['objective_cache_coeffs'] = self.coeffs.copy()
            dmem_key_in_list = ['cache']
            dmem_arg_in_list = ['cache']
            dmem_val_in_list = [cache]
            mpi_map("reset_cache_minimize_kl_divergence",
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj='tm', obj_val=d2.transport_map,
                    mpi_pool=self.mpi_pool,
                    concatenate=False)
        # Evaluate KL-divergence
        bcast_tuple = (['d1', 'batch_size', 'd1_entropy'],
                       [None, batch_size[0], False])
        dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_val_in_list = [x, w, d2, params1, params2, cache]
        reduce_obj = SumChunkReduce(axis=0)
        out = mpi_map(kl_divergence, 
                      bcast_tuple=bcast_tuple,
                      dmem_key_in_list=dmem_key_in_list,
                      dmem_arg_in_list=dmem_arg_in_list,
                      dmem_val_in_list=dmem_val_in_list,
                      reduce_obj=reduce_obj,
                      mpi_pool=self.mpi_pool)
        if params['regularization'] == None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += params['regularization']['alpha'] * \
                   npla.norm( a - d2.transport_map.get_identity_coeffs() ,2)**2.
        elif params['regularization']['type'] == 'L1':
            # using ||a||_1 regularization (not squared)
            centered_coeffs = a - d2.transport_map.get_identity_coeffs() 
            weighted_a = params['regularization']['alpha']*params['regularization']['l1_weights']*centered_coeffs
            out += npla.norm(weighted_a,1)
            #print(params['regularization']['alpha'] * params['regularization']['l1_weights'])
        # LOGGING
        self.logger.debug("KL Obj. Eval. %d - KL-divergence = %.10e" % (params['nobj'], out))
        # if self.logger.getEffectiveLevel() <= logging.DEBUG:
        #     gx = np.min(d2.transport_map.grad_x(x))
        #     self.logger.debug("KL-evaluation %d - min(grad_x) = %e" % (
        #         params['nobj'], min_gx))
        return out

    def minimize_kl_divergence_grad_a_objective(self, a, params):
        r""" Gradient of the objective function :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` for the KL-divergence minimization.

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          params (dict): dictionary of parameters
        """
        params['nda_obj'] += 1
        x = params['x']
        w = params['w']
        d1 = params['d1']
        d2 = params['d2']
        params1 = params['params1']
        params2 = params['params2']
        cache = params['cache']
        batch_size = params['batch_size']
        # Update distribution coefficients
        d2.coeffs = a
        bcast_tuple = (['coeffs'],[a])
        mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
                obj='d2', obj_val=d2,
                mpi_pool=self.mpi_pool, concatenate=False)
        # Reset cache
        if (params['objective_cache_coeffs'] != self.coeffs).any():
            params['objective_cache_coeffs'] = self.coeffs.copy()
            dmem_key_in_list = ['cache']
            dmem_arg_in_list = ['cache']
            dmem_val_in_list = [cache]
            mpi_map("reset_cache_minimize_kl_divergence",
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj='tm', obj_val=d2.transport_map,
                    mpi_pool=self.mpi_pool,
                    concatenate=False)
        # Evaluate grad_a KL-divergence
        bcast_tuple = (['d1', 'batch_size'],
                       [None, batch_size[1]])
        dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_val_in_list = [x, w, d2, params1, params2, cache]
        reduce_obj = SumChunkReduce(axis=0)
        out = mpi_map(grad_a_kl_divergence, 
                      bcast_tuple=bcast_tuple,
                      dmem_key_in_list=dmem_key_in_list,
                      dmem_arg_in_list=dmem_arg_in_list,
                      dmem_val_in_list=dmem_val_in_list,
                      reduce_obj=reduce_obj,
                      mpi_pool=self.mpi_pool)
        if params['regularization'] == None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += params['regularization']['alpha'] \
                   * 2. * (a - d2.transport_map.get_identity_coeffs())
        elif params['regularization']['type'] == 'L1':
            alpha_reg = params['regularization']['alpha']*params['regularization']['l1_weights']
            # if only scalar is prescribed, set alpha as vector of equal values
            #if np.isscalar(alpha_reg):
            #    alpha_reg = alpha_reg*np.ones(len(a))
            tol_l1    = params['regularization']['tol_l1']
            centered_coeffs = a - d2.transport_map.get_identity_coeffs()
            for i_a, x_a in enumerate(centered_coeffs):
                if np.abs(x_a) >= tol_l1:
                    out[i_a] += alpha_reg[i_a] * np.sign(x_a)
                elif np.abs(x_a) < tol_l1 and out[i_a] < -1. * alpha_reg[i_a]:
                    out[i_a] += alpha_reg[i_a]
                elif np.abs(x_a) < tol_l1 and out[i_a] > 1. * alpha_reg[i_a]:
                    out[i_a] -= alpha_reg[i_a]
                elif np.abs(x_a) < tol_l1 and np.abs(out[i_a]) <= 1. * alpha_reg[i_a]:
                    out[i_a] = 0.

        if params['grad_check']:
            da = 1e-4
            fdg = FD.grad_a_fd(self.minimize_kl_divergence_objective, a, da, params)
            maxerr = np.max(np.abs(out - fdg))
            if maxerr > da and self.logger.getEffectiveLevel() <= logging.WARNING:
                self.logger.warning("Grad_a KL-evaluation %d - " % params['nda_obj'] + \
                                    "grad_a check FAIL - " + \
                                    "maxerr=%e (da=%e)" % (maxerr, da))
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("KL Grad_a Obj. Eval. %d - ||grad_a KLdiv|| = %.10e" % (
                params['nda_obj'], npla.norm(out)))
        # if self.logger.getEffectiveLevel() <= logging.DEBUG:
        #     self.logger.debug("KL-evaluation %d - grad_a KLdiv = \n%s" % (
        #         params['nda_obj'], out))
        return out

    def minimize_kl_divergence_tuple_grad_a_objective(self, a, params):
        r""" Function evaluation and gradient of the objective :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` for the KL-divergence minimization.

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          params (dict): dictionary of parameters
        """
        params['nobj'] += 1
        params['nda_obj'] += 1
        x = params['x']
        w = params['w']
        d1 = params['d1']
        d2 = params['d2']
        params1 = params['params1']
        params2 = params['params2']
        cache = params['cache']
        batch_size = params['batch_size']
        # Update distribution coefficients
        d2.coeffs = a
        bcast_tuple = (['coeffs'],[a])
        mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
                obj='d2', obj_val=d2,
                mpi_pool=self.mpi_pool, concatenate=False)
        # Reset cache
        if (params['objective_cache_coeffs'] != self.coeffs).any():
            params['objective_cache_coeffs'] = self.coeffs.copy()
            dmem_key_in_list = ['cache']
            dmem_arg_in_list = ['cache']
            dmem_val_in_list = [cache]
            mpi_map("reset_cache_minimize_kl_divergence",
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj='tm', obj_val=d2.transport_map,
                    mpi_pool=self.mpi_pool,
                    concatenate=False)
        # Evaluate grad_a KL-divergence
        bcast_tuple = (['d1', 'batch_size', 'd1_entropy'],
                       [None, batch_size[1], False])
        dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_val_in_list = [x, w, d2, params1, params2, cache]
        reduce_obj = TupleSumChunkReduce(axis=0)
        ev, ga = mpi_map(tuple_grad_a_kl_divergence, 
                         bcast_tuple=bcast_tuple,
                         dmem_key_in_list=dmem_key_in_list,
                         dmem_arg_in_list=dmem_arg_in_list,
                         dmem_val_in_list=dmem_val_in_list,
                         reduce_obj=reduce_obj,
                         mpi_pool=self.mpi_pool)
        if params['regularization'] == None:
            pass
        elif params['regularization']['type'] == 'L2':
            ev += params['regularization']['alpha'] * \
                  npla.norm(a - d2.transport_map.get_identity_coeffs(),2)**2.
            ga += params['regularization']['alpha'] \
                  * 2. * (a - d2.transport_map.get_identity_coeffs())
        if params['grad_check']:
            da = 1e-4
            fdg = FD.grad_a_fd(self.minimize_kl_divergence_objective, a, da, params)
            maxerr = np.max(np.abs(out - fdg))
            if maxerr > da and self.logger.getEffectiveLevel() <= logging.WARNING:
                self.logger.warning("Grad_a KL-evaluation %d - " % params['nda_obj'] + \
                                    "grad_a check FAIL - " + \
                                    "maxerr=%e (da=%e)" % (maxerr, da))
        # LOGGING
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("KL Obj. Eval. %d - KL-divergence = %.10e" % (params['nobj'], ev))
            self.logger.debug("KL Grad_a Obj. Eval. %d - ||grad_a KLdiv|| = %.10e" % (
                params['nda_obj'], npla.norm(ga)))
        # if self.logger.getEffectiveLevel() <= logging.DEBUG:
        #     self.logger.debug("KL-evaluation %d - grad_a KLdiv = \n%s" % (
        #         params['nda_obj'], out))
        return ev, ga

    def minimize_kl_divergence_hess_a_objective(self, a, params):
        r""" Hessian of the objective function :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` for the KL-divergence minimization.

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          params (dict): dictionary of parameters
        """
        params['nda2_obj'] += 1
        x = params['x']
        w = params['w']
        d1 = params['d1']
        d2 = params['d2']
        params1 = params['params1']
        params2 = params['params2']
        cache = params['cache']
        batch_size = params['batch_size']
        # Update distribution coefficients
        d2.coeffs = a
        bcast_tuple = (['coeffs'],[a])
        mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
                obj='d2', obj_val=d2,
                mpi_pool=self.mpi_pool, concatenate=False)
        # Reset cache
        if (params['objective_cache_coeffs'] != self.coeffs).any():
            params['objective_cache_coeffs'] = self.coeffs.copy()
            dmem_key_in_list = ['cache']
            dmem_arg_in_list = ['cache']
            dmem_val_in_list = [cache]
            mpi_map("reset_cache_minimize_kl_divergence",
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj='tm', obj_val=d2.transport_map,
                    mpi_pool=self.mpi_pool,
                    concatenate=False)
        # Evaluate hess_a KL-divergence
        bcast_tuple = (['d1', 'batch_size'],
                       [None, batch_size[2]])
        dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_val_in_list = [x, w, d2, params1, params2, cache]
        reduce_obj = SumChunkReduce(axis=0)
        out = mpi_map(hess_a_kl_divergence, 
                      bcast_tuple=bcast_tuple,
                      dmem_key_in_list=dmem_key_in_list,
                      dmem_arg_in_list=dmem_arg_in_list,
                      dmem_val_in_list=dmem_val_in_list,
                      reduce_obj=reduce_obj,
                      mpi_pool=self.mpi_pool)
        if params['regularization'] == None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += np.diag( np.ones(d2.n_coeffs)*2.*params['regularization']['alpha'] )
        if params['hess_check']:
            da = 1e-4
            fdg = FD.grad_a_fd(self.minimize_kl_divergence_grad_a_objective, a, da, params)
            maxerr = np.max(np.abs(out - fdg))
            if maxerr > da:
                self.logger.warning("Hess_a KL-evaluation %d - " % params['nda2_obj'] + \
                                    "hess_a check FAIL - " + \
                                    "maxerr=%e (da=%e)" % (maxerr, da))
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("KL Hess_a Obj. Eval. %d " % params['nda2_obj'])
        # if self.logger.getEffectiveLevel() <= logging.DEBUG:
        #     import dill
        #     U,S,V = scila.svd(out)
        #     try:
        #         with open('svd.dat', 'rb') as stream:
        #             ll = dill.load(stream)
        #     except IOError:
        #         ll = []
        #     ll.append(S)
        #     with open('svd.dat', 'wb') as stream:
        #         dill.dump(ll, stream)
        return out

    def minimize_kl_divergence_action_hess_a_objective(self, a, da, params):
        r""" Action of the Hessian of the objective function :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` on the direction ``v``

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          da (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
            vector on which to apply the Hessian
          params (dict): dictionary of parameters
        """
        params['nda2_obj'] += 1
        x = params['x']
        w = params['w']
        d1 = params['d1']
        d2 = params['d2']
        params1 = params['params1']
        params2 = params['params2']
        cache = params['cache']
        batch_size = params['batch_size']
        # Update distribution coefficients
        d2.coeffs = a
        bcast_tuple = (['coeffs'],[a])
        mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
                obj='d2', obj_val=d2,
                mpi_pool=self.mpi_pool, concatenate=False)
        # Reset cache
        if (params['objective_cache_coeffs'] != self.coeffs).any():
            params['objective_cache_coeffs'] = self.coeffs.copy()
            dmem_key_in_list = ['cache']
            dmem_arg_in_list = ['cache']
            dmem_val_in_list = [cache]
            mpi_map("reset_cache_minimize_kl_divergence",
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj='tm', obj_val=d2.transport_map,
                    mpi_pool=self.mpi_pool,
                    concatenate=False)
        # Evaluate hess_a KL-divergence
        bcast_tuple = (['da','d1', 'batch_size'],
                       [da, None, batch_size[2]])
        dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
        dmem_val_in_list = [x, w, d2, params1, params2, cache]
        reduce_obj = SumChunkReduce(axis=0)
        out = mpi_map(action_hess_a_kl_divergence, 
                      bcast_tuple=bcast_tuple,
                      dmem_key_in_list=dmem_key_in_list,
                      dmem_arg_in_list=dmem_arg_in_list,
                      dmem_val_in_list=dmem_val_in_list,
                      reduce_obj=reduce_obj,
                      mpi_pool=self.mpi_pool)
        if params['regularization'] == None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += 2. * params['regularization']['alpha'] * da 
        elif params['regularization']['type'] == 'L1':
            # common to ignore effect of L1 on hessian of regularized objective
            out += 0.
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("KL Hess_a Obj. Eval. %d " % params['nda2_obj'])
        # if self.logger.getEffectiveLevel() <= logging.DEBUG:
        #     import dill
        #     U,S,V = scila.svd(out)
        #     try:
        #         with open('svd.dat', 'rb') as stream:
        #             ll = dill.load(stream)
        #     except IOError:
        #         ll = []
        #     ll.append(S)
        #     with open('svd.dat', 'wb') as stream:
        #         dill.dump(ll, stream)
        return out

    def minimize_kl_divergence_action_storage_hess_a_objective(self, a, v, params):
        r""" Assemble the Hessian :math:`\mathcal{D}_{KL}\left(\pi_1, \pi_{2,{\bf a}}\right)` and compute its action on the vector :math:`v`, for the KL-divergence minimization problem.

        Args:
          a (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients
          v (:class:`ndarray<numpy.ndarray>` [:math:`N`]): vector on which to apply the Hessian
          params (dict): dictionary of parameters
        """
        x = params['x']
        w = params['w']
        d1 = params['d1']
        d2 = params['d2']
        params1 = params['params1']
        params2 = params['params2']
        cache = params['cache']
        batch_size = params['batch_size']
        # Update distribution coefficients
        d2.coeffs = a
        bcast_tuple = (['coeffs'],[a])
        mpi_map("_set_coeffs", bcast_tuple=bcast_tuple,
                obj='d2', obj_val=d2,
                mpi_pool=self.mpi_pool, concatenate=False)
        # Reset cache
        if (params['objective_cache_coeffs'] != self.coeffs).any():
            params['objective_cache_coeffs'] = self.coeffs.copy()
            # Reset cache
            dmem_key_in_list = ['cache']
            dmem_arg_in_list = ['cache']
            dmem_val_in_list = [cache]
            mpi_map("reset_cache_minimize_kl_divergence",
                    dmem_key_in_list=dmem_key_in_list,
                    dmem_arg_in_list=dmem_arg_in_list,
                    dmem_val_in_list=dmem_val_in_list,
                    obj='tm', obj_val=d2.transport_map,
                    mpi_pool=self.mpi_pool,
                    concatenate=False)
        # Assemble Hessian
        if not params['hess_assembled']:
            # Assemble
            params['nda2_obj'] += 1
            bcast_tuple = (['d1', 'batch_size'],
                           [None, batch_size[2]])
            dmem_key_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
            dmem_arg_in_list = ['x', 'w', 'd2', 'params1', 'params2', 'cache']
            dmem_val_in_list = [x, w, d2, params1, params2, cache]
            dmem_key_out_list = ['hess_a_kl_divergence']
            (params['hess_a_kl_divergence'], ) = mpi_map_alloc_dmem(
                storage_hess_a_kl_divergence, 
                bcast_tuple=bcast_tuple, dmem_key_in_list=dmem_key_in_list,
                dmem_arg_in_list=dmem_arg_in_list, dmem_val_in_list=dmem_val_in_list,
                dmem_key_out_list=dmem_key_out_list,
                mpi_pool=self.mpi_pool, concatenate=False)
            params['hess_assembled'] = True
            if self.logger.getEffectiveLevel() <= logging.DEBUG:
                self.logger.debug("KL Storage Hess_a Obj. Eval. %d " % params['nda2_obj'])
        params['nda2_obj_dot'] += 1
        # Evaluate the action of hess_a KL-divergence
        bcast_tuple = (['v'], [v])
        dmem_key_in_list = ['hess_a_kl_divergence']
        dmem_arg_in_list = ['H']
        dmem_val_in_list = [params['hess_a_kl_divergence']]
        reduce_obj = SumChunkReduce(axis=0)
        out = mpi_map(action_stored_hess_a_kl_divergence,
                      bcast_tuple=bcast_tuple,
                      dmem_key_in_list=dmem_key_in_list,
                      dmem_arg_in_list=dmem_arg_in_list,
                      dmem_val_in_list=dmem_val_in_list,
                      reduce_obj=reduce_obj,
                      mpi_pool=self.mpi_pool)
        if params['regularization'] == None:
            pass
        elif params['regularization']['type'] == 'L2':
            out += 2.*params['regularization']['alpha'] * v
        # if self.logger.getEffectiveLevel() <= logging.DEBUG:
        #     self.logger.debug("KL Action Hess_a Obj. Eval. %d " % params['nda2_obj_dot'] + \
        #                      "- v^T H v = %.10e" % np.dot(out,v))
        return out

    def minimize_kl_divergence_callback(self, xk):
        self.it_callback += 1
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            self.logger.debug("Iteration %d" % self.it_callback)
        if self.ders_callback == 2:
            self.params_callback['hess_assembled'] = False
        
    def regression(self, t, tparams=None, d=None, qtype=None, qparams=None,
                   x=None, w=None, x0=None,
                   regularization=None, tol=1e-4, maxit=100,
                   batch_size_list=None, mpi_pool_list=None):
        r""" Compute :math:`{\bf a}^* = \arg\min_{\bf a} \Vert T - T({\bf a}) \Vert_{\pi}`.

        This regression problem can be completely decoupled if the measure
        is a product measure, obtaining

        .. math::

           a^{(i)*} = \arg\min_{\bf a^{(i)}} \Vert T_i - T_i({\bf a}^{(i)}) \Vert_{\pi_i}

        Args:
          t (function or :class:`ndarray<numpy.ndarray>` [:math:`m`]): function
            :math:`t` with signature ``t(x)`` or its functions values
          tparams (dict): parameters for function :math:`t`
          d (Distribution): distribution :math:`\pi`
          qtype (int): quadrature type to be used for the approximation of
            :math:`\mathbb{E}_{\pi}`
          qparams (object): parameters necessary for the construction of the
            quadrature
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): quadrature points
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          w (:class:`ndarray<numpy.ndarray>` [:math:`m`]): quadrature weights
            used for the approximation of :math:`\mathbb{E}_{\pi}`
          x0 (:class:`ndarray<numpy.ndarray>` [:math:`N`]): coefficients to be used
            as initial values for the optimization
          regularization (dict): defines the regularization to be used.
            If ``None``, no regularization is applied.
            If key ``type=='L2'`` then applies Tikonhov regularization with
            coefficient in key ``alpha``.
          tol (float): tolerance to be used to solve the regression problem.
          maxit (int): maximum number of iterations
          batch_size_list (:class:`list<list>` [d] :class:`tuple<tuple>` [3] :class:`int<int>`):
            Each of the tuples in the list corresponds to each component of the map.
            The entries of the tuple define whether to evaluate the regression 
            in batches of a certain size or not. 
            A size ``1`` correspond to a completely
            non-vectorized evaluation. A size ``None`` correspond to a
            completely vectorized one. (Note: if ``nprocs > 1``, then the batch
            size defines the size of the batch for each process)
          mpi_pool_list (:class:`list<list>` [d] :class:`mpi_map.MPI_Pool` or ``None``):
            pool of processes to be used for function evaluation, gradient evaluation and
            Hessian evaluation for each component of the approximation.
            Value ``None`` will use serial evaluation.

        Returns:
          (:class:`list<list>` [:math:`d`]) containing log information from the
          optimizer.

        .. seealso:: :mod:`MonotonicApproximation`

        .. note:: the resulting coefficients :math:`{\bf a}` are automatically
           set at the end of the optimization. Use :func:`get_coeffs` in order
           to retrieve them.

        .. note:: The parameters ``(qtype,qparams)`` and ``(x,w)`` are mutually
           exclusive, but one pair of them is necessary.
        """
        if batch_size_list is None:
            batch_size_list = [(None,None,None)] * self.dim_out
        if mpi_pool_list is None:
            mpi_pool_list = [None] * self.dim_out
        if (x is None) and (w is None):
            (x,w) = d.quadrature(qtype, qparams)
        if isinstance(t, np.ndarray):
            T = t
        else:
            T = t(x)
        
        log_entry_list = []
        start_x0 = 0
        reg = None
        for i,(a,avar, batch_size_tuple, mpi_pool) in enumerate(zip(
                self.approx_list,self.active_vars, batch_size_list, mpi_pool_list)):
            if regularization is not None and regularization['type'] == 'L2':
                reg = {'type': 'L2',
                       'alpha': a.n_coeffs * regularization['alpha'] / self.n_coeffs }
            x0a = None
            if x0 is not None:
                x0a = x0[start_x0:start_x0+a.n_coeffs]
                start_x0 += a.n_coeffs
            (coeffs, log_entry) = a.regression( T[:,i], x=x[:,avar], w=w, x0=x0a,
                                                regularization=reg, tol=tol,
                                                maxit=maxit,
                                                batch_size=batch_size_tuple,
                                                mpi_pool=mpi_pool)
            log_entry_list.append( log_entry )
            if not log_entry['success']:
                break
        return log_entry_list

    @staticmethod
    def from_xml(node):
        raise NotImplementedError("To be implemented")

class InverseTransportMap(TransportMap):
    r""" Given the transport map :math:`T`, define :math:`S=T^{-1}`.

    Args:
      tm (:class:`TransportMap`): map :math:`T`
    """
    def __init__(self, tm):
        self.tm = tm
        self.dim_in = self.tm.dim_in
        self.dim_out = self.tm.dim_out
        self.dim = self.tm.dim

    def get_ncalls_tree(self, indent=""):
        out = super(InverseTransportMap, self).get_ncalls_tree(indent)
        out += self.tm.get_ncalls_tree(indent + "  ")
        return out

    def get_nevals_tree(self, indent=""):
        out = super(InverseTransportMap, self).get_nevals_tree(indent)
        out += self.tm.get_nevals_tree(indent + "  ")
        return out

    def get_teval_tree(self, indent=""):
        out = super(InverseTransportMap, self).get_teval_tree(indent)
        out += self.tm.get_teval_tree(indent + "  ")
        return out

    def update_ncalls_tree(self, obj):
        super(InverseTransportMap, self).update_ncalls_tree(obj)
        self.tm.update_ncalls_tree( obj.tm )

    def update_nevals_tree(self, obj):
        super(InverseTransportMap, self).update_nevals_tree(obj)
        self.tm.update_nevals_tree( obj.tm )

    def update_teval_tree(self, obj):
        super(InverseTransportMap, self).update_teval_tree(obj)
        self.tm.update_teval_tree( obj.tm )

    def reset_counters(self):
        super(InverseTransportMap, self).reset_counters()
        self.tm.reset_counters()
        
    @property
    def n_coeffs(self):
        r""" Returns the total number of coefficients.

        Returns:
           total number :math:`N` of coefficients characterizing the transport map.
        """
        return self.tm.n_coeffs

    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.
        """
        return self.tm.coeffs
        
    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps

        Raises:
           ValueError: if the number of input coefficients does not match the
              number of required coefficients :func:`n_coeffs`.
        """
        self.tm.coeffs = coeffs

    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), *args, **kwargs):
        r""" Evaluate the transport map at the points :math:`{\bf x} \in \mathbb{R}^{m \times d}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- transformed points

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return self.tm.inverse(x)

    @counted
    def inverse(self, x, *args, **kwargs):
        r""" Compute: :math:`\hat{S}^{-1}({\bf y},{\bf a})`

        Args:
           y (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T^{-1}({\bf y},{\bf a})` for every evaluation point
        """
        return self.tm.evaluate(x)

    @counted
    def grad_x_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf x} \hat{S}^{-1}({\bf x},{\bf a}) = \nabla_{\bf x} T({\bf x},{\bf a})`.

        This is
        
        .. math::
            :nowrap:

            \nabla_{\bf x} T({\bf x},{\bf a}) =
                 \begin{bmatrix}
                 \nabla_{\bf x}  T_1({\bf x},{\bf a})  \\
                 \nabla_{\bf x}  T_2({\bf x},{\bf a})  \\
                 \vdots \\
                 \nabla_{\bf x}  T_d({\bf x},{\bf a})
                 \end{bmatrix}

        for every evaluation point.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           gradient matrices for every evaluation point.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return self.tm.grad_x(x)

    @counted
    def hess_x_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla^2_{\bf x} \hat{S}^{-1}({\bf x},{\bf a}) = \nabla^2_{\bf x} T({\bf x},{\bf a})`.

        This is the tensor

        .. math::

           \left[\nabla^2_{\bf x} T({\bf x},{\bf a})\right]_{i,k,:,:} = \nabla^2_{\bf x} T_k({\bf x}^{(i)},{\bf a}^{(k)})

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return self.tm.hess_x(x)

    @counted
    def grad_a(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a} \hat{S}({\bf x},{\bf a})`

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
        return self.tm.grad_a_inverse(x)

    @counted
    def grad_a_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf a} \hat{S}^{-1}({\bf x},{\bf a}) = \nabla_{\bf a} T({\bf x},{\bf a})`

        By the definition of the transport map :math:`T({\bf x},{\bf a})`,
        the components :math:`T_1 ({\bf x}_1, {\bf a}^{(1)})`,
        :math:`T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`, ...
        are defined by different sets of parameters :math:`{\bf a}^{(1)}`,
        :math:`{\bf a}^{(2)}`, etc.

        For this reason :math:`\nabla_{\bf a} T({\bf x},{\bf a})`
        is block diagonal:

        .. math::
           :nowrap:

           \nabla_a T({\bf x},{\bf a}) = \begin{bmatrix}
           \left[ \nabla_{{\bf a}^{(1)}} T_1 ({\bf x}_1, {\bf a}^{(1)}) \right]^T & {\bf 0} & \cdots \\
           {\bf 0} & \left[ \nabla_{{\bf a}^{(2)}} T_2 ({\bf x}_{1:2}, {\bf a}^{(2)}) \right]^T & \\
           \vdots & & \ddots
           \end{bmatrix}

        Consequentely this function will return only the diagonal blocks of the gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`list<list>` of :class:`ndarray<numpy.ndarray>` [:math:`n_i`]) --
              list containing
              :math:`\nabla_{{\bf a}^{(1)}} T_1 ({\bf x}_1, {\bf a}^{(1)})`,
              :math:`\nabla_{{\bf a}^{(2)}} T_2 ({\bf x}_{1:2}, {\bf a}^{(2)})`,
              etc.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        return self.tm.grad_a(x)
        
class CompositeTransportMap(CompositeMap):
    r"""
    .. deprecate:: 2.0
       Use :class:`CompositeMap` instead
    """
    @deprecate("TransportMaps.Maps.CompositeTransportMaps",
               "2.0",
               "Use TransportMaps.Maps.CompositeMap instead")
    def __init__(self, *args, **kwargs):
        super(CompositeTransportMap, self).__init__(*args, **kwargs)

class ListCompositeTransportMap(ListCompositeMap):
    r"""
    .. deprecate:: 2.0
       Use :class:`ListCompositeMap` instead
    """
    @deprecate("TransportMaps.Maps.ListCompositeTransportMaps",
               "2.0",
               "Use TransportMaps.Maps.ListCompositeMap instead")
    def __init__(self, *args, **kwargs):
        super(ListCompositeTransportMap, self).__init__(*args, **kwargs)

class ListStackedTransportMap(ListStackedMap, TransportMap):
    r"""
    .. deprecate:: 2.0
       Use :class:`ListStackedMap` instead
    """
    @deprecate("TransportMaps.Maps.ListStackedTransportMaps",
               "2.0",
               "Use TransportMaps.Maps.ListStackedMap instead")
    def __init__(self, *args, **kwargs):
        super(ListStackedTransportMap, self).__init__(*args, **kwargs)
