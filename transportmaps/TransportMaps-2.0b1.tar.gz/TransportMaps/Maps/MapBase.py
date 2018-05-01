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

from TransportMaps.Misc import deprecate, counted, cached, cached_tuple, get_sub_cache
from TransportMaps.ObjectBase import TMO
from TransportMaps.Functionals.FunctionBase import Function
from TransportMaps.Distributions.DistributionBase import ProductDistribution
from TransportMaps.Functionals.ProductDistributionParametricPullbackComponentFunctionBase import ProductDistributionParametricPullbackComponentFunction

__all__ = ['Map', 'ParametricMap',
           'LinearMap', 'ConditionallyLinearMap', 'ConstantMap',
           'CompositeMap',
           'ListCompositeMap',
           'ListStackedMap']

nax = np.newaxis

class Map(TMO):
    r""" Abstract map :math:`T:\mathbb{R}^{d_x}\rightarrow\mathbb{R}^{d_y}`

    Args:
      dim_in (int): input dimension :math:`d_x`
      dim_out (int): output dimension :math:`d_y`
    """
    def __init__(self, dim_in, dim_out):
        super(Map, self).__init__()
        self.dim_in = dim_in
        self.dim_out = dim_out
        self.dim = None
        if self.dim_in == self.dim_out:
            self.dim = self.dim_in

    def __call__(self, x):
        r"""
        Calls :func:`evaluate`.
        """
        return self.evaluate( x )

    @cached()
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the map :math:`T` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached()
    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the gradient :math:`\nabla_{\bf x}T` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_x`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached_tuple(['evaluate','grad_x'])
    @counted
    def tuple_grad_x(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the function and gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`tuple`) -- function and gradient evaluation

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached(caching=False)
    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the Hessian :math:`\nabla^2_{\bf x}T` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_x,d_x`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @cached(caching=False)
    @counted
    def action_hess_x(self, x, dx, precomp=None, idxs_slice=slice(None), **kwargs):
        r""" [Abstract] Evaluate the action of the Hessian :math:`\langle\nabla^2_{\bf x}T,\delta{\bf x}\rangle` at the points :math:`{\bf x} \in \mathbb{R}^{m \times d_x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y,d_x`]) -- transformed points

        Raises:
          NotImplementedError: to be implemented in sub-classes
        """
        raise NotImplementedError("To be implemented in sub-classes")

    @counted
    def pushforward(self, x, pi, params_t=None, params_pi=None, idxs_slice=slice(None),
                    cache=None):
        r""" Compute: :math:`\pi \circ T_{\bf a}^{-1}({\bf y}) \vert\det \grad_{\bf x}T_{\bf a}^{-1}({\bf y})\vert`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pushed forward
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
           cache (dict): cache

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\pi \circ T^{-1}({\bf y,a}) \vert\det \grad_{\bf x}T^{-1}({\bf y,a})\vert`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return np.exp( self.log_pushforward(x, pi, params_t=params_t, params_pi=params_pi,
                                            idxs_slice=idxs_slice, cache=cache) )

    @counted
    def pullback(self, x, pi, params_t=None, params_pi=None, idxs_slice=slice(None),
                 cached=None):
        r""" Compute: :math:`\pi \circ T({\bf x,a}) \vert\det \grad_{\bf x}T({\bf x,a})\vert`.

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
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\pi \circ T({\bf x,a}) \vert\det \grad_{\bf x}T({\bf x,a})\vert`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        return np.exp( self.log_pullback(x, pi, params_t, params_pi, idxs_slice, cache) )

    def _evaluate_log_transport(self, lpdf, ldgx):
        return lpdf + ldgx

    @cached([('pi',None),('t',None)])
    @counted
    def log_pullback(self, x, pi, params_t=None, params_pi=None, idxs_slice=slice(None),
                     cache=None):
        r""" Compute: :math:`\log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert`.

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
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        # Init sub-cache if necessary
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        ev = self.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        ldgx = self.log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        lpdf = pi.log_pdf(ev, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)
        return self._evaluate_log_transport(lpdf, ldgx)

    @counted
    def log_pushforward(self, x, pi, params_t=None, params_pi=None, idxs_slice=slice(None),
                        *args, **kwargs):
        r""" Compute :math:`\log \pi \circ T^{-1}({\bf x},{\bf a}) + \log \vert \det D T^{-1}({\bf y},{\bf a}) \vert`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pulled back        
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \pi \circ T^{-1}({\bf x},{\bf a}) + \log \vert \det D T^{-1}({\bf y},{\bf a}) \vert`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        if params_t is None:
            params_t = {'components': [{} for i in range(self.dim_out)]}
        xinv = self.inverse(x, precomp=params_t, idxs_slice=idxs_slice)
        params_t['xinv'] = xinv
        ldgx = self.log_det_grad_x_inverse(x, precomp=params_t, idxs_slice=idxs_slice)
        lpdf = pi.log_pdf(xinv, params=params_pi)
        return self._evaluate_log_transport(lpdf, ldgx)

    def _evaluate_grad_x_log_transport(self, gxlpdf, gx, gxldgx):
        return np.einsum('...i,...ij->...j', gxlpdf, gx) + gxldgx

    @cached([('pi',None),('t',None)])
    @counted
    def grad_x_log_pullback(self, x, pi, params_t=None, params_pi=None,
                            idxs_slice=slice(None), cache=None, *args, **kwargs):
        r""" Compute: :math:`\nabla_{\bf x}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right]`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pulled back        
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right]`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_pullback`, :func:`grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        ev = self.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        gx = self.grad_x(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        gxldgx = self.grad_x_log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        gxlpdf = pi.grad_x_log_pdf(
            ev, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)
        return self._evaluate_grad_x_log_transport(gxlpdf, gx, gxldgx)

    @cached_tuple(['log_pullback', 'grad_a_log_pullback'],[('pi',None),('t',None)])
    @counted
    def tuple_grad_x_log_pullback(self, x, pi, params_t=None, params_pi=None,
                                  idxs_slice=slice(None), cache=None, *args, **kwargs):
        r""" Compute: :math:`\left(\log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert, \nabla_{\bf x}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right]\right)`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pulled back        
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`tuple`) --
            :math:`\left(\log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert, \nabla_{\bf x}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right]\right)`

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_pullback`, :func:`grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        ev = self.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        ldgx = self.log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        gx = self.grad_x(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        gxldgx = self.grad_x_log_det_grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        lpdf, gxlpdf = pi.tuple_grad_x_log_pdf(
            ev, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache)
        return ( self._evaluate_log_transport(lpdf, ldgx),
                 self._evaluate_grad_x_log_transport(gxlpdf, gx, gxldgx) )

    @cached([('pi',None),('t',None)], False)
    @counted
    def hess_x_log_pullback(self, x, pi, params_t=None, params_pi=None,
                            idxs_slice=slice(None), cache=None, *args, **kwargs):
        r""" Compute :math:`\nabla^2_{\bf x}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right]`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pulled back        
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right]`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_x_log_pullback`, :func:`log_pullback`, :func:`grad_x`, :func:`hess_x` and :func:`hess_x_log_det_grad_x`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        n = x.shape[0]
        if issubclass(type(pi), ProductDistribution):
            hess_x_sum = np.zeros((n,self.dim,self.dim))
            # currently not using parallel implementation (batch_size_list, mpi_pool_list)
            # currently using params_t and params_pi assuming None
            for i,(a,avars) in enumerate(zip(self.approx_list,self.active_vars)):
                pi_i = pi.get_component([i])
                pS_i = ProductDistributionParametricPullbackComponentFunction(a, pi_i)
                hess_x_sum[np.ix_(range(n),avars,avars)] += pS_i.hess_x(x[:,avars])
            return hess_x_sum
        else:
            xval = self.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
            dxT = self.grad_x(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
            dx2logpi = pi.hess_x_log_pdf(
                xval, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache) # n x d x d
            A = np.einsum('...ij,...ik->...jk', dx2logpi, dxT) # n x d x d
            A = np.einsum('...ij,...ik->...jk', A, dxT) # n x d x d
            dxlogpi = pi.grad_x_log_pdf(
                xval, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache) # n x d
            dx2T = self.hess_x(
                x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache) # n x d x d x d
            B = np.einsum('...i,...ijk->...jk', dxlogpi, dx2T)
            C = self.hess_x_log_det_grad_x(
                x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
            return A + B + C

    @cached([('pi',None),('t',None)], False)
    @counted
    def action_hess_x_log_pullback(self, x, pi, dx, params_t=None, params_pi=None,
                                   idxs_slice=slice(None), cache=None, *args, **kwargs):
        r""" Compute :math:`\langle\nabla^2_{\bf x}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right],\delta{\bf x}\rangle`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pulled back        
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\langle\nabla^2_{\bf x}\left[ \log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert \right],\delta{\bf x}\rangle`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_x_log_pullback`, :func:`log_pullback`, :func:`grad_x`, :func:`hess_x` and :func:`hess_x_log_det_grad_x`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        pi_cache, t_cache = get_sub_cache(cache, ('pi',None), ('t',None))
        n = x.shape[0]
        xval = self.evaluate(x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        dxT = self.grad_x(
            x, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache) # n x d x d

        A = np.einsum('...ij,...j->...i', dxT, dx) # n x d
        A = pi.action_hess_x_log_pdf(
            xval, A, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache) # n x d
        A = np.einsum('...ij,...i->...j', dxT, A)

        dxlogpi = pi.grad_x_log_pdf(
            xval, params=params_pi, idxs_slice=idxs_slice, cache=pi_cache) # n x d
        B = self.action_hess_x(
            x, dx, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache) # n x d x d
        B = np.einsum('...i,...ij->...j', dxlogpi, B)

        C = self.action_hess_x_log_det_grad_x(
            x, dx, precomp=params_t, idxs_slice=idxs_slice, cache=t_cache)
        
        return A + B + C

    @counted
    def grad_x_log_pushforward(self, x, pi, params_t=None, params_pi=None,
                               idxs_slice=slice(None), *args, **kwargs):
        r""" Compute: :math:`\nabla_{\bf x}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \vert\det \nabla_{\bf x}T^{-1}({\bf x,a})\vert \right]`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pulled back        
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \vert\det \nabla_{\bf x}T^{-1}({\bf x,a})\vert \right]`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_pushforward`, :func:`grad_x_inverse` and :func:`grad_x_log_det_grad_x_inverse`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        inv = self.inverse(x)
        gxinv = self.grad_x_inverse(x)
        gxldgxinv = self.grad_x_log_det_grad_x_inverse(x, params_t)
        gxlpdfinv = pi.grad_x_log_pdf(inv, params_pi)
        return self._evaluate_grad_x_log_transport(gxlpdfinv, gxinv, gxldgxinv)
        # return np.einsum( '...i,...ij->...j',
        #                   pi.grad_x_log_pdf(self.inverse(x), params_pi),
        #                   self.grad_x_inverse(x) ) \
        #     + self.grad_x_log_det_grad_x_inverse(x, params_t)

    @counted
    def tuple_grad_x_log_pushforward(self, x, pi, params_t=None, params_pi=None,
                                     idxs_slice=slice(None), *args, **kwargs):
        r""" Compute: :math:`\left(\log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert, \nabla_{\bf x}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \vert\det \nabla_{\bf x}T^{-1}({\bf x,a})\vert \right]\right)`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pulled back        
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`tuple`) --
           :math:`\left(\log \pi \circ T({\bf x,a}) + \log \vert\det \nabla_{\bf x}T({\bf x,a})\vert, \nabla_{\bf x}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \vert\det \nabla_{\bf x}T^{-1}({\bf x,a})\vert \right]\right)`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_pushforward`, :func:`grad_x_inverse` and :func:`grad_x_log_det_grad_x_inverse`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        inv = self.inverse(x)
        gxinv = self.grad_x_inverse(x)
        ldgxinv = self.log_det_grad_x_inverse(x, params_t)
        gxldgxinv = self.grad_x_log_det_grad_x_inverse(x, params_t)
        lpdfinv, gxlpdfinv = pi.tuple_grad_x_log_pdf(inv, params_pi)
        return ( self._evaluate_log_transport(lpdfinv, ldgxinv),
                 self._evaluate_grad_x_log_transport(gxlpdfinv, gxinv, gxldgxinv) )

    @counted
    def hess_x_log_pushforward(self, x, pi, params_t=None, params_pi=None,
                               idxs_slice=slice(None), *args, **kwargs):
        r""" Compute :math:`\nabla^2_{\bf x}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \vert\det \nabla_{\bf x}T^{-1}({\bf x,a})\vert \right]`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pulled back       
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \vert\det \nabla_{\bf x}T^{-1}({\bf x,a})\vert \right]`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_x_log_pushforward`, :func:`log_pushforward`, :func:`grad_x_inverse`, :func:`hess_x_inverse` and :func:`hess_x_log_det_grad_x_inverse`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        n = x.shape[0]
        inv = self.inverse(x)
        dxT = self.grad_x_inverse(x) # n x d x d
        dx2logpi = pi.hess_x_log_pdf( inv, params_pi ) # n x d x d
        A = np.einsum('...ij,...ik->...jk', dx2logpi, dxT) # n x d x d
        A = np.einsum('...ij,...ik->...jk', A, dxT) # n x d x d
        dxlogpi = pi.grad_x_log_pdf(inv, params_pi) # n x d
        dx2T = self.hess_x_inverse(x) # n x d x d x d
        B = np.einsum('...i,...ijk->...jk', dxlogpi, dx2T)
        C = self.hess_x_log_det_grad_x_inverse(x)
        return A + B + C

    @counted
    def action_hess_x_log_pushforward(
            self, x, pi, dx, params_t=None, params_pi=None, idxs_slice=slice(None),
            *args, **kwargs):
        r""" Compute :math:`\langle \nabla^2_{\bf x}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \vert\det \nabla_{\bf x}T^{-1}({\bf x,a})\vert \right],\delta{\bf x}\rangle`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           pi (:class:`Distributions.Distribution`): distribution to be pulled back       
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           params_t (dict): parameters for the evaluation of :math:`T_{\bf a}`
           params_pi (dict): parameters for the evaluation of :math:`\pi`
           idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\langle \nabla^2_{\bf x}\left[ \log \pi \circ T^{-1}({\bf x,a}) + \log \vert\det \nabla_{\bf x}T^{-1}({\bf x,a})\vert \right],\delta{\bf x}\rangle`
            at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`grad_x_log_pushforward`, :func:`log_pushforward`, :func:`grad_x_inverse`, :func:`hess_x_inverse` and :func:`hess_x_log_det_grad_x_inverse`.
        """
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        # n = x.shape[0]
        inv = self.inverse(x)
        dxT = self.grad_x_inverse(x) # n x d x d

        A = np.einsum('...ij,...j->...i', dxT, dx) # n x d
        A = pi.action_hess_x_log_pdf(inv, A, params_pi) # n x d
        A = np.einsum('...ij,...i->...j', dxT, A)

        dxlogpi = pi.grad_x_log_pdf(inv, params_pi) # n x d
        B = self.action_hess_x_inverse(x, dx) # n x d x d
        B = np.einsum('...i,...ij->...j', dxlogpi, B)

        C = self.action_hess_x_log_det_grad_x_inverse(x, dx)
        return A + B + C


class ParametricMap(Map):
    r""" Abstract map :math:`T:\mathbb{R}^{d_a}\times\mathbb{R}^{d_x}\rightarrow\mathbb{R}^{d_y}`

    Args:
      dim_in (int): input dimension :math:`d_x`
      dim_out (int): output dimension :math:`d_y`
    """    
    @property
    def n_coeffs(self):
        r""" Returns the total number of coefficients.

        Returns:
          (:class:`int`) -- total number :math:`N` of
              coefficients characterizing the map.

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    @deprecate("ParametricMap.get_n_coeffs()", "1.0b3",
               "Use property ParametricMap.n_coeffs instead")
    def get_n_coeffs(self):
        return self.n_coeffs
        
    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    @deprecate("ParametricMap.get_coeffs()", "1.0b3",
               "Use property ParametricMap.coeffs instead")
    def get_coeffs(self):
        return self.coeffs
    
    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def _set_coeffs(self, coeffs):
        self.coeffs = coeffs

    @deprecate("ParametricMap.set_coeffs(value)", "1.0b3",
               "Use setter ParametricMap.coeffs = value instead.")
    def set_coeffs(self, coeffs):
        self.coeffs = coeffs

    def grad_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`\nabla_{\bf a} T({\bf x},{\bf a})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`ndarray<numpy.ndarray>`) -- gradient

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def hess_a(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`\nabla^2_{\bf a} T({\bf x},{\bf a})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`ndarray<numpy.ndarray>`) -- Hessian

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def action_hess_a(self, x, da, precomp=None, idxs_slice=slice(None)):
        r""" Compute :math:`\langle\nabla^2_{\bf a} T({\bf x},{\bf a}), \delta{\bf a}\rangle`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          da (:class:`ndarray<numpy.ndarray>` [:math:`N`]): direction
            on which to evaluate the Hessian
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.
          
        Returns:
           (:class:`ndarray<numpy.ndarray>`) -- action of the Hessian

        Raises:
          NotImplementedError: needs to be implemented in subclasses
        """
        raise NotImplementedError("Must be implemented in subclasses")
        
class LinearMap(Map):
    r""" Map :math:`T({\bf x}) = {\bf c} + {\bf T} {\bf x}`

    Args:
      c (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): constant part
      T (:class:`ndarray<numpy.ndarray>` [:math:`d_y,d_x`]): linear part (matrix)
    """
    def __init__(self, c, T):
        if c.shape[0] != T.shape[0]:
            raise ValueError("The dimensions of the constant and the " + \
                             "linear part must match")
        super(LinearMap, self).__init__(T.shape[1], T.shape[0])
        self._c = c
        self._T = T

    @property
    def c(self):
        return self._c

    @property
    def T(self):
        return self._T

    @counted
    def evaluate(self, x, *args, **kwargs):
        return self.c + self.T.dot(x.T).T

    @counted
    def grad_x(self, x, *args, **kwargs):
        return self.T[:,:]

    @counted
    def hess_x(self, x, *args, **kwargs):
        return np.zeros((self.dim_out, self.dim_in, self.dim_in))

    @counted
    def action_hess_x(self, x, dx, *args, **kwargs):
        return np.zeros((self.dim_out, self.dim_in))

class ConditionallyLinearMap(Map):
    r""" Map :math:`T:\mathbb{R}^{d_x}\times\mathbb{R}^{d_a}\rightarrow\mathbb{R}^{d_y}` defined by :math:`T({\bf x};{\bf a}) = {\bf c}({\bf a}) + {\bf T}({\bf a}) {\bf x}`

    Args:
      c (:class:`Map`): map :math:`{\bf c}:\mathbb{R}^{d_a}\rightarrow\mathbb{R}^{d_y}`
      T (:class:`Map`):
        map :math:`{\bf T}:\mathbb{R}^{d_a}\rightarrow\mathbb{R}^{d_y\times d_x}`
      coeffs (:class:`ndarray<numpy.ndarray>`): fixing the coefficients :math:`{\bf a}` defining
        :math:`{\bf c}({\bf a})` and :math:`{\bf T}({\bf a})`.
    """
    def __init__(self, c, T, coeffs=None):
        if c.dim_in != T.dim_in:
            raise ValueError("Input dimension mismatch between c and T")
        if T.dim_out % c.dim_out != 0:
            raise ValueError("Output dimension mismatch between c and T")
        self._n_coeffs = c.dim_in
        self._cMap = c
        self._TMap = T
        din = T.dim_out // c.dim_out
        dout = c.dim_out
        super(ConditionallyLinearMap,self).__init__(
            din + self.n_coeffs, dout)
        self._coeffs = None
        self.coeffs = coeffs
        
    @property
    def c(self):
        return self._c

    @property
    def T(self):
        return self._T
        
    @property
    def n_coeffs(self):
        return self._n_coeffs

    @property
    def dim_lin(self):
        return self.dim_in - self.n_coeffs

    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.
        """
        return self._coeffs

    @coeffs.setter
    def coeffs(self, coeffs):
        r""" Set the coefficients.

        Args:
           coeffs (:class:`ndarray<numpy.ndarray>` [:math:`N`]):
              coefficients for the various maps
        """
        if coeffs is None:
            self._coeffs = None
        elif self._coeffs is None or np.any(self._coeffs != coeffs):
            self._c = self._cMap.evaluate(coeffs[nax,:])[0,:]
            self._T = self._TMap.evaluate(coeffs[nax,:])[0,:,:]
            try:
                self._grad_a_c = self._cMap.grad_x(coeffs[nax,:])[0,:,:]
                self._grad_a_T = self._TMap.grad_x(coeffs[nax,:])[0,:,:,:]
            except NotImplementedError:
                self._grad_a_c = None
                self._grad_a_T = None
            try:
                self._hess_a_c = self._cMap.hess_x(coeffs[nax,:])[0,:,:,:]
                self._hess_a_T = self._TMap.hess_x(coeffs[nax,:])[0,:,:,:,:]
            except NotImplementedError:
                self._hess_a_c = None
                self._hess_a_T = None
            self._coeffs = coeffs

    @property
    def grad_a_c(self):
        return self._grad_a_c

    @property
    def grad_a_T(self):
        return self._grad_a_T

    @property
    def hess_a_c(self):
        return self._hess_a_c

    @property
    def hess_a_T(self):
        return self._hess_a_T

    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        r""" Evaluate the map :math:`T` at the points :math:`{\bf x}`.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]) -- transformed points
        """
        if self._coeffs is None:
            m = x.shape[0]
            out = np.zeros((m,self.dim_out))
            for i in range(m):
                cf = x[[i],self.dim_lin:]
                xx = x[i,:self.dim_lin]
                c = self._cMap.evaluate(cf)[0,:]
                T = self._TMap.evaluate(cf)[0,:,:]
                out[i,:] = c + np.dot(T, xx)
        else:
            xx = x[:,:self.dim_lin]
            out = self.c + np.dot(self.T, xx.T).T
        return out

    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        if self._coeffs is None:
            m = x.shape[0]
            out = np.zeros((m,self.dim_out, self.dim_in))
            for i in range(m):
                cf = x[[i],self.dim_lin:]
                xx = x[i,:self.dim_lin]
                T = self._TMap.evaluate(cf)[0,:,:]
                gac = self._cMap.grad_x(cf)[0,:,:]
                gaT = self._TMap.grad_x(cf)[0,:,:,:]
                out[i,:,:self.dim_lin] = T
                out[i,:,self.dim_lin:] = gac + np.einsum('ijk,j->ik', gaT, xx)
        else:
            raise NotImplementedError("To be done")
        return out
        
class ConstantMap(Map):
    r""" Map :math:`T({\bf x})={\bf c}`

    Args:
       dim_in (int): input dimension :math:`d_x`
       const (:class:`ndarray<numpy.ndarray>`): constant :math:`{\bf c}`
    """
    def __init__(self, dim_in, const):
        self._const = const
        super(ConstantMap, self).__init__(dim_in, const.size)

    @property
    def const(self):
        return self._const

    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None)):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        # tpl = tuple([nax] + [slice(None)] * self._const.ndim)
        return self._const[:]

    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None)):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        # shp = (1,) + self._const.shape + (self.dim_in,)
        shp = self._const.shape + (self.dim_in,)
        return np.zeros(shp)

    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None)):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        # shp = (1,) + self._const.shape + (self.dim_in,self.dim_in)
        shp = self._const.shape + (self.dim_in,self.dim_in)
        return np.zeros(shp)

class ListCompositeMap(Map):
    r""" Construct the composite map :math:`T_1 \circ T_2 \circ \cdots \circ T_n`

    Args:
      tm_list (list): list of transport maps :math:`[T_1,\ldots,T_n]`

    ..warning:: This should become the standard ``CompositeTransportMap``, thus
                replacing the actual implementation.
    """
    def __init__(self, tm_list):
        if len(tm_list)==0:
            raise ValueError("There should be at least a map in the list")
        self.dim_in = tm_list[-1].dim_in
        dim_out_old = tm_list[-1].dim_out
        for tm in reversed(tm_list[:-1]):
            if tm.dim_in != dim_out_old:
                raise ValueError("The transport maps must have consistent dimensions!")
            dim_out_old = tm.dim_out
        self.dim_out = dim_out_old
        self.dim = None
        if self.dim_in == self.dim_out:
            self.dim = self.dim_in
        self.tm_list = tm_list

    def get_ncalls_tree(self, indent=""):
        out = Map.get_ncalls_tree(self, indent)
        for i, tm in enumerate(self.tm_list):
            out += tm.get_ncalls_tree(indent + " T%d - " % i)
        return out

    def get_nevals_tree(self, indent=""):
        out = Map.get_nevals_tree(self, indent)
        for i, tm in enumerate(self.tm_list):
            out += tm.get_nevals_tree(indent + " T%d - " % i)
        return out

    def get_teval_tree(self, indent=""):
        out = Map.get_teval_tree(self, indent)
        for i, tm in enumerate(self.tm_list):
            out += tm.get_teval_tree(indent + " T%d - " % i)
        return out

    def update_ncalls_tree(self, obj):
        super(ListCompositeMap, self).update_ncalls_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.tm_list, obj.tm_list)):
            tm.update_ncalls_tree(obj_tm)

    def update_nevals_tree(self, obj):
        super(ListCompositeMap, self).update_nevals_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.tm_list, obj.tm_list)):
            tm.update_nevals_tree(obj_tm)

    def update_teval_tree(self, obj):
        super(ListCompositeMap, self).update_teval_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.tm_list, obj.tm_list)):
            tm.update_teval_tree(obj_tm)
        
    def reset_counters(self):
        super(ListCompositeMap, self).reset_counters()
        for tm in self.tm_list:
            tm.reset_counters()
        
    @property
    def n_maps(self):
        return len(self.tm_list)

    @property
    def n_coeffs(self):
        r""" Returns the total number of coefficients.

        Returns:
           total number :math:`N` of coefficients characterizing the transport map.
        """
        return sum( [tm.n_coeffs for tm in self.tm_list] )

    @property
    def coeffs(self):
        r""" Returns the actual value of the coefficients.

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`N`]) -- coefficients.
        """
        return np.hstack( [ tm.coeffs for tm in self.tm_list ] )
        
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
        if len(coeffs) != self.n_coeffs:
            raise ValueError("Mismatch in the number of coefficients")
        start = 0
        for tm in self.tm_list:
            stop = start + tm.n_coeffs
            tm.coeffs = coeffs[start:stop]
            start = stop

    @cached([('tm_list',"n_maps")])
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
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
        tm_list_cache = get_sub_cache(cache, ('tm_list',self.n_maps))
        Xcp = x.copy()
        for tm, tm_cache in zip(reversed(self.tm_list),reversed(tm_list_cache)):
            Xcp = tm.evaluate(Xcp, idxs_slice=idxs_slice, cache=tm_cache)

        return Xcp

    @counted
    def inverse(self, x, *args, **kwargs):
        r""" Compute: :math:`T^{-1}({\bf y},{\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`T^{-1}({\bf y},{\bf a})` for every evaluation point
        """
        inv = x
        for tm in self.tm_list:
            inv = tm.inverse(inv)
        return inv

    @cached([('tm_list',"n_maps")])
    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\nabla_{\bf x} T({\bf x},{\bf a})`.

        Apply chain rule.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           gradient matrices for every evaluation point.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        tm_list_cache = get_sub_cache(cache, ('tm_list',self.n_maps)) 
        gx_next = self.tm_list[-1].grad_x(
            x, idxs_slice=idxs_slice, cache=tm_list_cache[-1])
        if len(self.tm_list) > 1:
            ev_next = self.tm_list[-1].evaluate(
                x, idxs_slice=idxs_slice, cache=tm_list_cache[-1])
        for i in range(len(self.tm_list)-2,-1,-1):
            tm = self.tm_list[i]
            tm_cache = tm_list_cache[i]
            gx = tm.grad_x(ev_next, idxs_slice=idxs_slice, cache=tm_cache)
            gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
            if i > 0:
                # Update ev_next
                ev_next = tm.evaluate( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
        return gx_next

    @cached_tuple(['evaluate','grad_x'],[('tm_list',"n_maps")])
    @counted
    def tuple_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Evaluate the function and gradient.

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points
          precomp (:class:`dict<dict>`): dictionary of precomputed values
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
           (:class:`tuple`) -- function and gradient evaluation
        """
        tm_list_cache = get_sub_cache(cache, ('tm_list',self.n_maps))
        ev_next, gx_next = self.tm_list[-1].tuple_grad_x(
            x, idxs_slice=idxs_slice, cache=tm_list_cache[-1])
        for i in range(len(self.tm_list)-2,-1,-1):
            tm = self.tm_list[i]
            tm_cache = tm_list_cache[i]
            ev_next, gx = tm.tuple_grad_x(ev_next, idxs_slice=idxs_slice, cache=tm_cache)
            gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
        return ev_next, gx_next

    @counted
    def grad_x_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla_{\bf x} T^{-1}({\bf x},{\bf a})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           gradient matrices for every evaluation point.
        """
        gx_next = self.tm_list[0].grad_x_inverse( x )
        if len(self.tm_list) > 1:
            ev_next = self.tm_list[0].inverse(x)
        for i in range(1, len(self.tm_list)):
            tm = self.tm_list[i]
            gx = tm.grad_x_inverse(ev_next)
            gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
            if i > 0:
                # Update ev_next
                ev_next = tm.inverse( ev_next )
        return gx_next

    @cached([('tm_list',"n_maps")],False)
    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\nabla^2_{\bf x} T({\bf x},{\bf a})`.

        Apply chain rule.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        tm_list_cache = get_sub_cache(cache, ('tm_list',self.n_maps))
        hx_next = self.tm_list[-1].hess_x(
            x, idxs_slice=idxs_slice, cache=tm_list_cache[-1])
        if len(self.tm_list) > 1:
            ev_next = self.tm_list[-1].evaluate(
                x, idxs_slice=idxs_slice, cache=tm_list_cache[-1])
            gx_next = self.tm_list[-1].grad_x(
                x, idxs_slice=idxs_slice, cache=tm_list_cache[-1] )
        for i in range(len(self.tm_list)-2,-1,-1):
            tm = self.tm_list[i]
            tm_cache = tm_list_cache[i]
            hx = tm.hess_x(ev_next, idxs_slice=idxs_slice, cache=tm_cache) # m x d x d x d
            gx = tm.grad_x(ev_next, idxs_slice=idxs_slice, cache=tm_cache) # m x d x d
            hx_next = np.einsum('...ij,...jkl->...ikl', gx, hx_next)
            tmp = np.einsum('...ijk,...jl->...ikl', hx, gx_next)
            hx_next += np.einsum('...ikl,...km->...ilm', tmp, gx_next)
            if i > 0:
                # Update gx_next
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                ev_next = tm.evaluate( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
        return hx_next

    @cached([('tm_list',"n_maps")],False)
    @counted
    def action_hess_x(self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute :math:`\langle\nabla^2_{\bf x} T({\bf x},{\bf a}), \delta{\bf x}\rangle`.

        Apply chain rule.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           action of the Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        tm_list_cache = get_sub_cache(cache, ('tm_list',self.n_maps))
        ahx_next = self.tm_list[-1].action_hess_x(
            x, dx, idxs_slice=idxs_slice, cache=tm_list_cache[-1]) # m x d x d
        if len(self.tm_list) > 1:
            ev_next = self.tm_list[-1].evaluate(
                x, idxs_slice=idxs_slice, cache=tm_list_cache[-1] )
            gx_next = self.tm_list[-1].grad_x(
                x, idxs_slice=idxs_slice, cache=tm_list_cache[-1] )
        for i in range(len(self.tm_list)-2,-1,-1):
            tm = self.tm_list[i]
            tm_cache = tm_list_cache[i]
            gx = tm.grad_x(ev_next, idxs_slice=idxs_slice, cache=tm_cache) # m x d x d
            ahx_next = np.einsum('...ij,...jk->...ik', gx, ahx_next) # m x d x d
            tmp = np.einsum('...jl,...l->...j', gx_next, dx) # m x d
            tmp = tm.action_hess_x(
                ev_next, tmp, idxs_slice=idxs_slice, cache=tm_cache) # m x d x d
            ahx_next += np.einsum('...jl,...ij->...il', gx_next, tmp) # m x d x d
            if i > 0:
                # Update gx_next
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                ev_next = tm.evaluate( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
        return ahx_next

    @counted
    def hess_x_inverse(self, x, *args, **kwargs):
        r""" Compute :math:`\nabla^2_{\bf x} T^{-1}({\bf x},{\bf a})`.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        hx_next = self.tm_list[0].hess_x_inverse(x)
        if len(self.tm_list) > 1:
            ev_next = self.tm_list[0].inverse( x )
            gx_next = self.tm_list[0].grad_x_inverse( x )
        for i in range(1,len(self.tm_list)):
            tm = self.tm_list[i]
            hx = tm.hess_x_inverse(ev_next) # m x d x d x d
            gx = tm.grad_x_inverse(ev_next) # m x d x d
            hx_next = np.einsum('...ij,...jkl->...ikl', gx, hx_next)
            tmp = np.einsum('...ijk,...jl->...ikl', hx, gx_next)
            hx_next += np.einsum('...ikl,...km->...ilm', tmp, gx_next)
            if i > 0:
                # Update gx_next
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                # update ev_next
                ev_next = tm.inverse( ev_next )
        return hx_next

    @counted
    def action_hess_x_inverse(self, x, dx, *args, **kwargs):
        r""" Compute :math:`\langle\nabla^2_{\bf x} T^{-1}({\bf x},{\bf a}), \delta{\bf x}\rangle`.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d,d`]) --
           action of the Hessian matrices for every evaluation point and every dimension.

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.
        """
        ahx_next = self.tm_list[0].action_hess_x_inverse(x, dx)
        if len(self.tm_list) > 1:
            ev_next = self.tm_list[0].inverse( x )
            gx_next = self.tm_list[0].grad_x_inverse( x )
        for i in range(1,len(self.tm_list)):
            tm = self.tm_list[i]
            gx = tm.grad_x_inverse(ev_next) # m x d x d
            ahx_next = np.einsum('...ij,...jk->...ik', gx, ahx_next)
            tmp = np.einsum('...jl,...l->...j', gx_next, dx) # m x d
            tmp = tm.action_hess_x_inverse(ev_next, tmp) # m x d x d
            ahx_next += np.einsum('...jl,...ij->...il', gx_next, tmp)
            if i > 0:
                # Update gx_next
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                # update ev_next
                ev_next = tm.inverse( ev_next )
        return ahx_next

    @cached([('tm_list',"n_maps")])
    @counted
    def log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})`.

        For the transport maps :math:`T_1,T_2`,

        .. math::

           \log \det \nabla_{\bf x} (T_1 \circ T_2)({\bf x}) = \log \det \nabla_{\bf x} T_1 ({\bf y}) + \log \det \nabla_{\bf x} T_2({\bf x})

        where :math:`{\bf y} = T_2({\bf x})`.

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T({\bf x}, {\bf a})` at every
           evaluation point
        """
        tm_list_cache = get_sub_cache(cache, ('tm_list',self.n_maps))

        Xcp = x.copy()
        log_det = np.zeros( Xcp.shape[0] )

        for tm, tm_cache in zip(reversed(self.tm_list),reversed(tm_list_cache)):
            log_det += tm.log_det_grad_x(Xcp, idxs_slice=idxs_slice, cache=tm_cache)
            Xcp = tm.evaluate(Xcp, idxs_slice=idxs_slice, cache=tm_cache)

        return log_det

    @cached([('tm_list',"n_maps")])
    @counted
    def grad_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x`.
        """
        tm_list_cache = get_sub_cache(cache, ('tm_list',self.n_maps))
        gx_ldet_next = self.tm_list[-1].grad_x_log_det_grad_x(
            x, idxs_slice=idxs_slice, cache=tm_list_cache[-1])
        if len(self.tm_list) > 1:
            ev_next = self.tm_list[-1].evaluate(
                x, idxs_slice=idxs_slice, cache=tm_list_cache[-1])
            gx_next = self.tm_list[-1].grad_x(
                x, idxs_slice=idxs_slice, cache=tm_list_cache[-1])
        for i in range(len(self.tm_list)-2,-1,-1):
            tm = self.tm_list[i]
            tm_cache = tm_list_cache[i]
            gx_ldet = tm.grad_x_log_det_grad_x(
                ev_next, idxs_slice=idxs_slice, cache=tm_cache)
            gx_ldet_next += np.einsum('...i,...ik->...k', gx_ldet, gx_next)
            if i > 0:
                # Update gx_next
                gx = tm.grad_x( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                # Update ev_next
                ev_next = tm.evaluate( ev_next, idxs_slice=idxs_slice, cache=tm_cache )
        return gx_ldet_next

    @counted
    def log_det_grad_x_inverse(self, x, precomp=None, *args, **kwargs):
        r""" Compute: :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})` at every
           evaluation point
        """
        ldet_next = self.tm_list[0].log_det_grad_x_inverse(x)
        if len(self.tm_list) > 1:
            ev_next = self.tm_list[0].inverse(x)
        for i in range(1,len(self.tm_list)):
            tm = self.tm_list[i]
            ldet_next += tm.log_det_grad_x_inverse(ev_next)
            if i < len(self.tm_list)-1:
                # Update ev_next
                ev_next = tm.inverse(ev_next)
        return ldet_next

    @counted
    def grad_x_log_det_grad_x_inverse(self, x, precomp=None, *args, **kwargs):
        r""" Compute: :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`.
        
        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
           :math:`\nabla_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})` at every
           evaluation point
        """
        gx_ldet_next = self.tm_list[0].grad_x_log_det_grad_x_inverse(x)
        if len(self.tm_list) > 1:
            ev_next = self.tm_list[0].inverse(x)
            gx_next = self.tm_list[0].grad_x_inverse(x)
        for i in range(1,len(self.tm_list)):
            tm = self.tm_list[i]
            gx_ldet = tm.grad_x_log_det_grad_x_inverse(ev_next)
            gx_ldet_next += np.einsum('...i,...ik->...k', gx_ldet, gx_next)
            if i < len(self.tm_list)-1:
                # Update gx_next
                gx = tm.grad_x_inverse( ev_next )
                gx_next = np.einsum('...ji,...ik->...jk', gx, gx_next)
                # Update ev_next
                ev_next = tm.inverse( ev_next )
        return gx_ldet_next

class CompositeMap(ListCompositeMap):
    r""" Given maps :math:`T_1,T_2`, define map :math:`T=T_1 \circ T_2`.

    Args:
      t1 (:class:`Map`): map :math:`T_1`
      t2 (:class:`Map`): map :math:`T_2`
    """
    def __init__(self, t1, t2):
        super(CompositeMap, self).__init__( [t1, t2] )
        self.t1 = self.tm_list[0]
        self.t2 = self.tm_list[1]

    @cached([('tm_list',"n_maps")],False)
    @counted
    def hess_x_log_det_grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`

        For the transport maps :math:`T_1,T_2`,

        .. math::

           \nabla^2_{\bf x} \log \det \nabla_{\bf x} (T_1 \circ T_2) = \left[ \nabla^2_{\bf x} \log \det (\nabla_{\bf x} T_1 \circ T_2) \cdot \nabla_{\bf x} T_2 + \nabla_{\bf x} \log \det \nabla_{\bf x} T_2 \right] \cdot (\nabla_{\bf x} T_2) + \nabla_{\bf x} \log \det (\nabla_{\bf x} T_1 \circ T_2) \cdot \nabla^2_{\bf x} T_2 + \nabla^2_{\bf x} \log \det \nabla_{\bf x} T_2

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        try:
            t1_cache = cache['tm_list_cache'][0]
            t2_cache = cache['tm_list_cache'][1]
        except TypeError:
            t1_cache = None
            t2_cache = None
        ev_t2 = self.t2.evaluate(x, cache=t2_cache) # m x d
        gx_t2 = self.t2.grad_x(x, cache=t2_cache)   # m x d x d
        hx_t2 = self.t2.hess_x(x, cache=t2_cache)   # m x d x d x d
        gx_ldet_gx_t1 = self.t1.grad_x_log_det_grad_x( ev_t2, cache=t1_cache ) # m x d
        hx_ldet_gx_t1 = self.t1.hess_x_log_det_grad_x( ev_t2, cache=t1_cache ) # m x d x d
        hx_ldet_gx_t2 = self.t2.hess_x_log_det_grad_x(x, cache=t2_cache) # m x d x d
        out = np.einsum('...ij,...jl->...il', hx_ldet_gx_t1, gx_t2)
        out = np.einsum('...ij,...il->...jl', gx_t2, out)
        out += np.einsum('...i,...ijk->...jk', gx_ldet_gx_t1, hx_t2)
        out += hx_ldet_gx_t2
        return out

    @cached([('tm_list',"n_maps")],False)
    @counted
    def action_hess_x_log_det_grad_x(
            self, x, dx, precomp=None, idxs_slice=slice(None), cache=None):
        r""" Compute: :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a}), \delta{\bf x}\rangle`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
             :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T({\bf x}, {\bf a}), \delta{\bf x}\rangle` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`hess_x_log_det_grad_x`.
        """
        try:
            t1_cache = cache['tm_list_cache'][0]
            t2_cache = cache['tm_list_cache'][1]
        except TypeError:
            t1_cache = None
            t2_cache = None
        ev_t2 = self.t2.evaluate(x, cache=t2_cache) # m x d
        gx_t2 = self.t2.grad_x(x, cache=t2_cache)   # m x d x d
        A = np.einsum('...ij,...j->...i', gx_t2, dx) # m x d
        A = self.t1.action_hess_x_log_det_grad_x(ev_t2, A, cache=t1_cache) # m x d
        A = np.einsum('...ij,...i->...j', gx_t2, A) # m x d

        gx_ldet_gx_t1 = self.t1.grad_x_log_det_grad_x( ev_t2, cache=t1_cache ) # m x d
        B = self.t2.action_hess_x(x, dx, cache=t2_cache) # m x d x d
        B = np.einsum('...i,...ij->...j', gx_ldet_gx_t1, B) # m x d

        C = self.t2.action_hess_x_log_det_grad_x(x, dx, cache=t2_cache) # m x d

        return A + B + C

    @counted
    def hess_x_log_det_grad_x_inverse(self, x, precomp=None, *args, **kwargs):
        r""" Compute: :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a})`
           at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        t1_inv = self.t1.inverse(x) # m x d
        gx_t1_inv = self.t1.grad_x_inverse(x)   # m x d x d
        hx_t1_inv = self.t1.hess_x_inverse(x)   # m x d x d x d
        gx_ldet_gx_t2_inv = self.t2.grad_x_log_det_grad_x_inverse( t1_inv ) # m x d
        hx_ldet_gx_t2_inv = self.t2.hess_x_log_det_grad_x_inverse( t1_inv ) # m x d x d
        hx_ldet_gx_t1_inv = self.t1.hess_x_log_det_grad_x_inverse(x) # m x d x d
        out = np.einsum('...ij,...jl->...il', hx_ldet_gx_t2_inv, gx_t1_inv)
        out = np.einsum('...ij,...il->...jl', gx_t1_inv, out)
        out += np.einsum('...i,...ijk->...jk', gx_ldet_gx_t2_inv, hx_t1_inv)
        out += hx_ldet_gx_t1_inv
        return out

    @counted
    def action_hess_x_log_det_grad_x_inverse(self, x, dx, precomp=None, *args, **kwargs):
        r""" Compute: :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a}), \delta{\bf x}\rangle`

        Args:
           x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
           dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): direction
            on which to evaluate the Hessian
           precomp (:class:`dict<dict>`): dictionary of precomputed values

        Returns:
           (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
           :math:`\langle\nabla^2_{\bf x} \log \det \nabla_{\bf x} T^{-1}({\bf x}, {\bf a}), \delta{\bf x}\rangle` at every evaluation point

        Raises:
           ValueError: if :math:`d` does not match the dimension of the transport map.

        .. seealso:: :func:`log_det_grad_x` and :func:`grad_x_log_det_grad_x`.
        """
        t1_inv = self.t1.inverse(x) # m x d
        gx_t1_inv = self.t1.grad_x_inverse(x)   # m x d x d
        A = np.einsum('...ij,...j->...i', gx_t1_inv, dx) # m x d
        A = self.t2.action_hess_x_log_det_grad_x_inverse(t1_inv, A) # m x d
        A = np.einsum('...ij,...i->...j', gx_t1_inv, A) # m x d

        gx_ldet_gx_t2_inv = self.t2.grad_x_log_det_grad_x_inverse( t1_inv ) # m x d
        B = self.t1.action_hess_x_inverse(x, dx) # m x d x d
        B = np.einsum('...i,...ij->...j', gx_ldet_gx_t2_inv, B) # m x d

        C = self.t1.action_hess_x_log_det_grad_x_inverse(x, dx) # m x d

        return A + B + C
        
class ListStackedMap(Map):
    r""" Defines the map :math:`T` obtained by stacking :math:`T_1, T_2, \ldots`.

    .. math::

       T({\bf x}) = \left[
       \begin{array}{c}
       T_1({\bf x}_{0:d_1}) \\
       T_2({\bf x}_{0:d_2}) \\
       \vdots
       \end{array}
       \right]

    Args:
      tm_list (:class:`list` of :class:`Map`): list of transport maps :math:`T_i`
    """
    def __init__(self, tm_list):
        self.dim_in = max( [ tm.dim_in for tm in tm_list ] )
        self.dim_out = sum( [tm.dim_out for tm in tm_list] )
        if self.dim_in == self.dim_out:
            self.dim = self.dim_in
        self.tm_list = tm_list

    def get_ncalls_tree(self, indent=""):
        out = Map.get_ncalls_tree(self, indent)
        for i, tm in enumerate(self.tm_list):
            out += tm.get_ncalls_tree(indent + " T%d - " % i)
        return out

    def get_nevals_tree(self, indent=""):
        out = Map.get_nevals_tree(self, indent)
        for i, tm in enumerate(self.tm_list):
            out += tm.get_nevals_tree(indent + " T%d - " % i)
        return out

    def get_teval_tree(self, indent=""):
        out = Map.get_teval_tree(self, indent)
        for i, tm in enumerate(self.tm_list):
            out += tm.get_teval_tree(indent + " T%d - " % i)
        return out

    def update_ncalls_tree(self, obj):
        super(ListStackedMap, self).update_ncalls_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.tm_list, obj.tm_list)):
            tm.update_ncalls_tree(obj_tm)

    def update_nevals_tree(self, obj):
        super(ListStackedMap, self).update_nevals_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.tm_list, obj.tm_list)):
            tm.update_nevals_tree(obj_tm)

    def update_teval_tree(self, obj):
        super(ListStackedMap, self).update_teval_tree(obj)
        for i, (tm, obj_tm) in enumerate(zip(self.tm_list, obj.tm_list)):
            tm.update_teval_tree(obj_tm)
        
    def reset_counters(self):
        super(ListStackedMap, self).reset_counters()
        for tm in self.tm_list:
            tm.reset_counters()
        
    @property
    def n_maps(self):
        return len(self.tm_list)

    @cached([('tm_list',"n_maps")])
    @counted
    def evaluate(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_list_cache = get_sub_cache(cache, ('tm_list',self.n_maps))
        out = np.zeros((x.shape[0], self.dim_out))
        start = 0
        for tm, tm_cache in zip(self.tm_list, tm_list_cache):
            stop = start + tm.dim_out
            out[:,start:stop] = tm.evaluate(x[:,:tm.dim_in], cache=tm_cache)
            start = stop
        return out

    @cached([('tm_list',"n_maps")])
    @counted
    def grad_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_list_cache = get_sub_cache(cache, ('tm_list',self.n_maps))
        out = np.zeros((x.shape[0], self.dim_out, self.dim_in))
        start = 0
        for tm, tm_cache in zip(self.tm_list, tm_list_cache):
            stop = start + tm.dim_out
            out[:,start:stop,:tm.dim_in] = tm.grad_x(x[:,:tm.dim_in], cache=tm_cache)
            start = stop
        return out

    @cached([('tm_list',"n_maps")],False)
    @counted
    def hess_x(self, x, precomp=None, idxs_slice=slice(None), cache=None):
        if x.shape[1] != self.dim_in:
            raise ValueError("dimension mismatch")
        tm_list_cache = get_sub_cache(cache, ('tm_list',self.n_maps))
        out = np.zeros((x.shape[0], self.dim_out, self.dim_in, self.dim_in))
        start = 0
        for tm, tm_cache in zip(self.tm_list, tm_list_cache):
            stop = start + tm.dim_out
            out[:,start:stop,:tm.dim_in,:tm.dim_in] = \
                tm.hess_x(x[:,:tm.dim_in], cache=tm_cache)
            start = stop
        return out