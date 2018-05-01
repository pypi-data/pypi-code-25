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

import copy
import dill
import numpy as np
import numpy.linalg as npla
import scipy.optimize as sciopt

import SpectralToolbox.Spectral1D as S1D

from .AdaptivityBase import Builder
from TransportMaps.Distributions import \
    PushForwardTransportMapDistribution, PullBackTransportMapDistribution
from TransportMaps.Routines import \
    laplace_approximation, grad_x_grad_t_kl_divergence, grad_t_kl_divergence
from TransportMaps.Misc import generate_total_order_midxs, \
    mpi_map, mpi_alloc_dmem, mpi_map_alloc_dmem, \
    ExpectationReduce, AbsExpectationReduce
from TransportMaps.Defaults import Default_LinearSpanTriangularTransportMap
from TransportMaps.Diagnostics.Routines import variance_approx_kl
from TransportMaps.Maps.FullTransportMaps import LinearTransportMap
from TransportMaps.Functionals.LinearSpanApproximationBase import \
    LinearSpanApproximation

__all__ = ['KullbackLeiblerBuilder',
           'SequentialKullbackLeiblerBuilder',
           'ToleranceSequentialKullbackLeiblerBuilder',
           'FirstVariationKullbackLeiblerBuilder']

nax = np.newaxis

class KullbackLeiblerBuilder(Builder):
    r""" Basis builder through minimization of kl divergence

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the parametric transport map :math:`T[{\bf a}]`,
    provides the functionalities to solve the problem

    .. math::

       \arg\min_{\bf a}\mathcal{D}_{\rm KL}\left(
       T[{\bf a}]_\sharp\rho \Vert \pi\right)

    up to a chosen tolerance.

    Args:
      base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\rho`
      target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\pi`
      transport_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
        transport map :math:`T`
      solve_params (dict): dictionary of parameters for solution
      validator (:class:`Validator<TransportMaps.Diagnostic.Validator>`):
        validator to be used to check stability of the solution
      callback (function): function taking a map and optional additional arguments
        which is called whenever it is deemed necessary by the chosen algorithm
        (e.g. for storing purposes)
      callback_kwargs (dict): additional arguments to be provided to the function
        ``callback``.
      verbosity (int): level of verbosity of the builder
    """
    def __init__(self, base_distribution, target_distribution,
                 transport_map, solve_params, validator=None,
                 callback=None, callback_kwargs={}, verbosity=0):
        self.base_distribution = base_distribution
        self.target_distribution = target_distribution
        self.transport_map = transport_map
        self.solve_params = solve_params
        self.validator = validator
        self.callback = callback
        self.callback_kwargs = callback_kwargs
        self.verbosity = verbosity
        super(KullbackLeiblerBuilder, self).__init__()

    def __getstate__(self):
        out = super(KullbackLeiblerBuilder, self).__getstate__()
        out.pop('callback', None)
        out.pop('callback_kwargs', None)
        return out

    def __setstate__(self, state):
        super(KullbackLeiblerBuilder, self).__setstate__(state)

    def set_mpi_pool(self, mpi_pool):
        self.solve_params['mpi_pool'] = mpi_pool
    
    def solve(self, reloading=False):
        r"""          
        Returns:
          (:class:`TransportMaps.Maps.TransportMap`) -- the transport map fitted.
        """
        if reloading:
            self.solve_params['x0'] = self.transport_map.coeffs
        if 'x0' not in self.solve_params or self.solve_params['x0'] is None:
            self.solve_params['x0'] = \
                self.transport_map.get_default_init_values_minimize_kl_divergence()
        if self.validator is None:
            pull_tar = PullBackTransportMapDistribution(
                self.transport_map, self.target_distribution)
            log = self.transport_map.minimize_kl_divergence(
                self.base_distribution, pull_tar, **self.solve_params)
            if not log['success']:
                self.transport_map.coeffs = self.solve_params['x0']
        else:
            log = self.validator.solve_to_tolerance(
                self.transport_map,
                self.base_distribution, self.target_distribution,
                self.solve_params)
        return self.transport_map, log

class SequentialKullbackLeiblerBuilder(KullbackLeiblerBuilder):
    r""" Solve over a list of maps, using the former to warm start the next one

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the list of parametric transport maps
    :math:`[T_1[{\bf a}_1,\ldots,T_n[{\bf a}_n]`,
    provides the functionalities to solve the problems

    .. math::

       \arg\min_{{\bf a}_i}\mathcal{D}_{\rm KL}\left(
       T_i[{\bf a}_i]_\sharp\rho \Vert \pi\right)

    up to a chosen tolerance, where the numerical solution for map
    :math:`T_{i+1}` is started at :math:`T_i`

    Args:
      base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\rho`
      target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\pi`
      transport_map_list (:class:`list` of :class:`TransportMap<TransportMaps.Maps.TransportMap>`):
        list of transports map :math:`T_i`
      solve_params_list (:class:`list` of :class:`dict`):
        list of dictionaries of parameters for solution
      validator (:class:`Validator<TransportMaps.Diagnostic.Validator>`):
        validator to be used to check stability of the solution
      regression_params_list (:class:`list` of :class:`dict`):
        list of dictionaries of parameters for the regression between :math:`T_i` and
        :math:`T_{i+1}`
      verbosity (int): level of verbosity of the builder
    """
    def __init__(self, base_distribution, target_distribution,
                 transport_map_list, solve_params_list,
                 validator=None, regression_params_list=None,
                 callback=None, callback_kwargs={}, verbosity=0):
        self.solve_counter = 0
        self.transport_map_list = transport_map_list
        self.solve_params_list = solve_params_list
        self.regression_params_list = regression_params_list
        super(SequentialKullbackLeiblerBuilder,
              self).__init__(
                  base_distribution, target_distribution,
                  transport_map_list[0], solve_params_list[0], validator,
                  callback=callback, callback_kwargs=callback_kwargs,
                  verbosity=verbosity)

    def set_mpi_pool(self, mpi_pool):
        for solve_params in self.solve_params_list:
            solve_params['mpi_pool'] = mpi_pool
        
    def solve(self, reloading=False):
        r"""
        Returns:
          (:class:`TransportMaps.Maps.TransportMap`) -- the last transport map fitted.
        """
        if not reloading:
            self.solve_counter = 0
        if self.solve_counter == 0:
            self.transport_map = self.transport_map_list[0]
            self.solve_params = self.solve_params_list[0]
            tm, log = super(SequentialKullbackLeiblerBuilder, self).solve()
            if not log['success']:
                tm.coeffs = x0
                return tm, log
            self.solve_counter += 1
        tm_old = self.transport_map_list[self.solve_counter-1]
        for self.transport_map, self.solve_params in zip(
                self.transport_map_list[self.solve_counter:],
                self.solve_params_list[self.solve_counter:]):
            # Here we are assuming nested basis
            for c1, c2 in zip(tm_old.approx_list, self.transport_map.approx_list):
                # Constant part
                for i1, midx1 in enumerate(c1.c.multi_idxs):
                    for i2, midx2 in enumerate(c2.c.multi_idxs):
                        if midx1 == midx2:
                            break
                    c2.c.coeffs[i2] = c1.c.coeffs[i1]
                # Integrated part
                for i1, midx1 in enumerate(c1.h.multi_idxs):
                    for i2, midx2 in enumerate(c2.h.multi_idxs):
                        if midx1 == midx2:
                            break
                    c2.h.coeffs[i2] = c1.h.coeffs[i1]
            # solve for the new map using regressed starting point
            self.solve_params['x0'] = self.transport_map.coeffs
            tm, log = super(SequentialKullbackLeiblerBuilder, self).solve()
            if not log['success']:
                return tm_old, log
            tm_old = tm
            self.solve_counter += 1
        return tm, log

class ToleranceSequentialKullbackLeiblerBuilder(KullbackLeiblerBuilder):
    r""" Solve over a list of maps, using the former to warm start the next one, until a target tolerance is met

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the list of parametric transport maps
    :math:`[T_1[{\bf a}_1,\ldots,T_n[{\bf a}_n]`,
    provides the functionalities to solve the problems

    .. math::

       \arg\min_{{\bf a}_i}\mathcal{D}_{\rm KL}\left(
       T_i[{\bf a}_i]_\sharp\rho \Vert \pi\right)

    up to a chosen tolerance, where the numerical solution for map
    :math:`T_{i+1}` is started at :math:`T_i`

    Args:
      base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\rho`
      target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\pi`
      transport_map_list (:class:`list` of :class:`TransportMap<TransportMaps.Maps.TransportMap>`):
        list of transports map :math:`T_i`
      solve_params_list (:class:`list` of :class:`dict`):
        list of dictionaries of parameters for solution
      regression_params_list (:class:`list` of :class:`dict`):
        list of dictionaries of parameters for the regression between :math:`T_i` and
        :math:`T_{i+1}`
      validator (:class:`Validator<TransportMaps.Diagnostic.Validator>`):
        validator to be used to check stability of the solution
      tol (float): target variance diagnostic tolerance
      var_diag_params (dict): parameters to be used in the variance diagnostic approximation
      callback (function): function taking a map and optional additional arguments
        which is called whenever it is deemed necessary by the chosen algorithm
        (e.g. for storing purposes)
      callback_kwargs (dict): additional arguments to be provided to the function
        ``callback``.
      verbosity (int): level of verbosity of the builder
    """
    def __init__(self, base_distribution, target_distribution,
                 transport_map_list, solve_params_list, validator=None,
                 tol=1e-2, var_diag_params=None, laplace_pull=False, 
                 callback=None, callback_kwargs={}, verbosity=0):
        self.solve_counter = 0
        self.transport_map_list = transport_map_list
        self.solve_params_list = solve_params_list
        self.tol = tol
        self.var_diag_params = var_diag_params
        self.laplace_pull = laplace_pull
        super(ToleranceSequentialKullbackLeiblerBuilder,
              self).__init__(
                  base_distribution, target_distribution,
                  transport_map_list[0], solve_params_list[0], validator,
                  callback=callback, callback_kwargs=callback_kwargs,
                  verbosity=verbosity)

    def set_mpi_pool(self, mpi_pool):
        for solve_params in self.solve_params_list:
            solve_params['mpi_pool'] = mpi_pool
        self.var_diag_params['mpi_pool_tuple'] = (None, mpi_pool)
        
    def solve(self, reloading=False):
        r"""
        Returns:
          (:class:`TransportMaps.Maps.TransportMap`) -- the last transport map fitted.
        """
        if not reloading:
            self.solve_counter = 0
        if self.solve_counter == 0:
            if self.var_diag_params is None:
                self.var_diag_params = {
                    'qtype': self.solve_params_list[-1]['qtype'],
                    'qparams': self.solve_params_list[-1]['qparams']}

            self.transport_map = self.transport_map_list[0]
            self.solve_params = self.solve_params_list[0]
                
            if self.laplace_pull:
                # First find Laplace point and center to it
                lap = laplace_approximation(self.target_distribution)
                lap_map = LinearTransportMap.build_from_Gaussian(lap)

                # Set initial conditions to Laplace approximation
                self.transport_map.regression(
                    lap_map, d=base_distribution,
                    qtype=3, qparams=[3]*base_distribution.dim,
                    regularization={'alpha': 1e-4, 'type': 'L2'})

                self.solve_params['x0'] = self.transport_map.coeffs

            tm, log = super(ToleranceSequentialKullbackLeiblerBuilder, self).solve()
            if not log['success']:
                tm.coeffs = x0
                return tm, log
            pull_tar = PullBackTransportMapDistribution(tm, self.target_distribution)
            var = variance_approx_kl(self.base_distribution, pull_tar,
                                     **self.var_diag_params)
            self.logger.info("Variance diagnostic: %e" % var)
            if var <= self.tol:
                return tm, log
            self.solve_counter += 1
        tm_old = self.transport_map_list[self.solve_counter-1]
        for self.transport_map, self.solve_params in zip(
                self.transport_map_list[self.solve_counter:],
                self.solve_params_list[self.solve_counter:]):
            # Here we are assuming nested basis
            for c1, c2 in zip(tm_old.approx_list, self.transport_map.approx_list):
                # Constant part
                for i1, midx1 in enumerate(c1.c.multi_idxs):
                    for i2, midx2 in enumerate(c2.c.multi_idxs):
                        if midx1 == midx2:
                            break
                    c2.c.coeffs[i2] = c1.c.coeffs[i1]
                # Integrated part
                for i1, midx1 in enumerate(c1.h.multi_idxs):
                    for i2, midx2 in enumerate(c2.h.multi_idxs):
                        if midx1 == midx2:
                            break
                    c2.h.coeffs[i2] = c1.h.coeffs[i1]
            
            # solve for the new map using regressed starting point
            self.solve_params['x0'] = self.transport_map.coeffs
            tm, log = super(ToleranceSequentialKullbackLeiblerBuilder, self).solve()
            if not log['success']:
                return tm_old, log
            pull_tar = PullBackTransportMapDistribution(tm, self.target_distribution)
            var = variance_approx_kl(self.base_distribution, pull_tar, **self.var_diag_params)
            self.logger.info("Variance diagnostic: %e" % var)
            if var <= self.tol:
                return tm, log
            tm_old = tm
            self.solve_counter += 1
        # Variance was not met
        log['success'] = False
        log['msg'] = "Desired tolerance was no met by the map adaptivity. " + \
                     "Target variance: %e - Variance: %e " % (self.tol, var)
        return tm, log

class FirstVariationKullbackLeiblerBuilder(KullbackLeiblerBuilder):
    r""" Adaptive builder based on the first variation of the kl divergence

    Given distribution :math:`\nu_\rho` and :math:`\nu_\pi`,
    and the parametric transport map :math:`T[{\bf a}]`,
    provides the functionalities to solve the problem

    .. math::

       \arg\min_{\bf a}\mathcal{D}_{\rm KL}\left(
       T[{\bf a}]_\sharp\rho \Vert \pi\right) =
       \arg\min_{\bf a}\underbrace{\mathbb{E}_\rho\left[
       -\log T[{\bf a}]^\sharp\pi \right]}_{
       \mathcal{J}[T]({\bf x})}

    up to a chosen tolerance, by enriching the map using information
    from the first variation

    .. math::

       \nabla\mathcal{J}[T]({\bf x}) =
       (\nabla_{\bf x}T)^{-\top}
       \left(\log\frac{\rho({\bf x})}{T^\sharp\pi({\bf x})}\right)

    Args:
      base_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\rho`
      target_distribution (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        distribution :math:`\nu_\pi`
      transport_map (:class:`TransportMap<TransportMaps.Maps.TransportMap>`):
        starting transport map :math:`T`
      validator (:class:`Validator<TransportMaps.Diagnostic.Validator>`):
        validator to be used to check stability of the solution
      eps_bull (float): target tolerance of variance diagnostic
      solve_params (dict): dictionary of parameters for solution
      callback (function): function taking a map and optional additional arguments
        which is called whenever it is deemed necessary by the chosen algorithm
        (e.g. for storing purposes)
      callback_kwargs (dict): additional arguments to be provided to the function
        ``callback``.
      verbosity (int): level of verbosity of the builder
    """
    def __init__(
            self, base_distribution, target_distribution,
            transport_map, validator, eps_bull, regression_builder=None,
            solve_params={}, line_search_params={},
            max_it=20, use_fv_hess=False, 
            prune_trunc=.01, avar_trunc=.1, coeff_trunc=.01,
            callback=None, callback_kwargs={}, verbosity=0):
        self.regression_builder = regression_builder
        self.eps_bull = eps_bull
        self.line_search_params = line_search_params
        self.max_it = max_it
        self.use_fv_hess = use_fv_hess
        self.prune_trunc = prune_trunc
        self.avar_trunc = avar_trunc
        self.coeff_trunc = coeff_trunc
        self.transport_map_list = []
        self.variance_diagnostic_list = []
        super(FirstVariationKullbackLeiblerBuilder,
              self).__init__(
                  base_distribution, target_distribution,
                  transport_map, solve_params, validator,
                  callback=callback, callback_kwargs=callback_kwargs,
                  verbosity=verbosity)
        
    def solve(self, reloading=False):
        if not reloading:
            self.iter_counter = 0
            self.adapt_stage = "validation" # validation, diagnostic, refinement
            self.tolmet = False
        spmet = True
        log = {}
        fv_adapt_status = 'success'
        self.logger.info(
            "Starting. Map structure:\n" + \
            map_structure_str(
                self.transport_map, indent='   ', verbosity=self.verbosity) + \
            map_sparsity_str(
                self.transport_map, indent='   ', verbosity=self.verbosity))
        while self.iter_counter < self.max_it and not self.tolmet:
            self.logger.info("Iteration %d" % self.iter_counter)
            if self.adapt_stage == 'validation':
                spmet = False
                while not spmet and \
                      not log.get('validator_cost_exceeded', False) and \
                      not log.get('validator_fcast_cost_exceeded', False):
                    self.logger.info("Validation...")
                    _, log = super(
                        FirstVariationKullbackLeiblerBuilder,
                        self).solve()
                    if not log.get('success', False) or \
                       log.get('validator_cost_exceeded', False) or \
                       log.get('validator_fcast_cost_exceeded', False):
                        if not log.get('success', True):
                            log['fv_adapt_status'] = 'Failed to converge'
                            self.logger.warning(
                                "KL-minimization failed to converge. " + \
                                "Reverting to the last available map.")
                        else:
                            log['fv_adapt_status'] = 'Cost exceeded'
                            self.logger.warning(
                                "Maximum cost exceeded. Reverting to the last available map.")
                        if len(self.transport_map_list) > 0:
                            return self.transport_map_list[-1], log
                        else:
                            return self.transport_map, log
                    self.transport_map_list.append( self.transport_map )
                    self.callback( self.transport_map, **self.callback_kwargs )
                    spmet = log.get('validator_error', 0.) < \
                            log.get('validator_target_error', np.inf)
                    if not spmet:
                        self.logger.info("Pruning...")
                        # Prune
                        tm_new = prune_map(
                            self.transport_map, log['validator_prune_params'],
                            self.prune_trunc)
                        self.logger.info(
                            "Map pruning. Map structure:\n" + \
                            map_structure_str(tm_new, indent='   ', verbosity=self.verbosity) + \
                            map_sparsity_str(tm_new, indent='   ', verbosity=self.verbosity))
                        if tm_new.n_coeffs == self.transport_map.n_coeffs:
                            # The minimum number of coefficients has already been reached
                            self.logger.warning(
                                "The pruning of the map, did not lead to the removal of " + \
                                "any degree of freedom."
                            )
                            log['fv_adapt_status'] = 'No pruning available'
                            log['fv_adapt_spmet'] = False
                            log['fv_adapt_tolmet'] = False
                            log['fv_adapt_it'] = it
                            if len(self.transport_map_list) > 0:
                                return self.transport_map_list[-1], log
                            else:
                                return self.transport_map, log
                        else:
                            self.transport_map = tm_new
                self.adapt_stage = 'diagnostic'
                self.callback( self.transport_map, **self.callback_kwargs )
            if self.adapt_stage == 'diagnostic':
                # Once the coefficients are determined we check whether the
                # variance diagnostic tolerance is met
                self.logger.info("Computing variance diagnostic...")
                pb_distribution = PullBackTransportMapDistribution(
                    self.transport_map, self.target_distribution)
                var_diag = variance_approx_kl(
                    self.base_distribution, pb_distribution,
                    qtype=self.solve_params['qtype'], qparams=self.solve_params['qparams'],
                    mpi_pool_tuple=(None, self.solve_params.get('mpi_pool')) )
                self.logger.info("Variance diagnostic: %.3e (target %.3e)" % (
                    var_diag,self.eps_bull))
                self.variance_diagnostic_list.append( var_diag )
                if len(self.variance_diagnostic_list) > 1 and \
                   var_diag > self.variance_diagnostic_list[-2]:
                    fv_adapt_status = \
                        "The variance diagnostic is not decreasing. This can be due to " + \
                        "several reasons:\n" + \
                        "   1) the number of quadrature points is insufficient and/or\n" + \
                        "   2) the validation tolerance is too low with respect to the " + \
                        "target adaptivity tolerance and/or\n" + \
                        "   3) a pruning step with too strict tolerance has occurred"
                    self.logger.warning(fv_adapt_status)
                    break
                self.tolmet = var_diag <= self.eps_bull
                self.adapt_stage = 'refinement'
                self.callback( self.transport_map, **self.callback_kwargs )
            if self.adapt_stage == 'refinement':
                if not self.tolmet: # Refinement
                    self.logger.info("Computing first variation...")
                    (x, w) = self.base_distribution.quadrature(
                        self.solve_params['qtype'], self.solve_params['qparams'])
                    # Compute first variation (here we need to make use of the caching)
                    pb_distribution = PullBackTransportMapDistribution(
                        self.transport_map, self.target_distribution)
                    gt, abs_exp_gxgt = compute_first_variation(
                        x, w, self.base_distribution, pb_distribution, self.use_fv_hess,
                        batch_size=self.solve_params.get('batch_size'),
                        mpi_pool=self.solve_params.get('mpi_pool'))
                    # Generate candidate transport map for regression of first variation
                    self.logger.info("Projection of first variation...")
                    fv_tri_tm = first_variation_candidate_triangular_map(
                        self.transport_map, abs_exp_gxgt, self.avar_trunc)
                    fv_tri_tm, log_reg1 = self.regression_builder.solve(
                        fv_tri_tm, gt, x=x, w=w)
                    # TODO: check log success
                    # Line search and evaluation of improved map
                    self.logger.info("Line search...")
                    tm_ev = self.transport_map.evaluate(x)
                    fv_tri_tm_ev = fv_tri_tm.evaluate(x)
                    tm_pxd = self.transport_map.partial_xd(x)
                    fv_tri_tm_pxd = fv_tri_tm.partial_xd(x)
                    delta, ls_success = kl_divergence_fv_line_search(
                        self.target_distribution, w,
                        tm_ev, fv_tri_tm_ev, tm_pxd, fv_tri_tm_pxd,
                        self.line_search_params, mpi_pool=self.solve_params.get('mpi_pool'))
                    if not ls_success:
                        fv_adapt_status = \
                            "Line search did not converge. This may mean several things:\n" + \
                            "   1) the maximum number of line search iterations is too low\n" + \
                            "   2) the validation tolerance is too low to " + \
                            "be able to detect improving directions\n" + \
                            "   3) the validation tolerance is too low to detect that " + \
                            "there is no other improving direction\n" + \
                            "   4) the validation tolerance is too low w.r.t the target " + \
                            "adaptivity tolerance"
                        self.logger.warning(fv_adapt_status)
                        break
                    # Generate candidate transport map for regression on improved map
                    self.logger.info("Generating new candidate map...")
                    tm_new = improved_candidate_map(self.transport_map, fv_tri_tm)
                    x0 = tm_new.coeffs
                    tm_new, log_reg2 = self.regression_builder.solve(
                        tm_new, tm_ev - delta * fv_tri_tm_ev,
                        x=x, w=w, x0=x0)
                    # TODO: check log success
                    # Remove unnecessary coefficients
                    coeffs_weights = np.abs(tm_new.coeffs)
                    coeffs_weights /= max(coeffs_weights)
                    tm_new = prune_map(tm_new, coeffs_weights, self.coeff_trunc)
                    self.logger.info(
                        "Map refinement. Map structure:\n" + \
                        map_structure_str(tm_new, indent='   ', verbosity=self.verbosity) + \
                        map_sparsity_str(tm_new, indent='   ', verbosity=self.verbosity))
                    if is_equal_map(self.transport_map, tm_new):
                        fv_adapt_status = \
                            "The refinement step did not change the original map. " + \
                            "This may be due to several factors:\n" + \
                            "   1) the truncation tolerances are too strict w.r.t. " + \
                            "the validation tolerances\n" + \
                            "   2) the validation tolerance is too low w.r.t the target " + \
                            "adaptivity tolerance"
                        self.logger.warning(fv_adapt_status)
                        break
                    # Set up as the new transport map and new initial conditions
                    self.transport_map = tm_new
                    self.solve_params['x0'] = self.transport_map.coeffs
                self.adapt_stage = 'validation'
            self.iter_counter += 1
            self.callback( self.transport_map, **self.callback_kwargs )
        if self.iter_counter == self.max_it:
            fv_adapt_status = 'Maximum number of iterations exceeded'
        log['fv_adapt_status'] = fv_adapt_status
        log['fv_adapt_tolmet'] = self.tolmet
        log['fv_adapt_spmet'] = spmet
        log['fv_adapt_it'] = self.iter_counter
        return self.transport_map, log

def compute_first_variation(
        x, w, d1, d2, use_fv_hess, batch_size=None, mpi_pool=None):
    # Distribute objects
    d2_distr = dill.loads( dill.dumps(d2) )
    d2_distr.reset_counters()
    mpi_alloc_dmem(d1=d1, d2=d2_distr, mpi_pool=mpi_pool)
    # Link tm to d2.transport_map
    def link_tm_d2(d2):
        return (d2.transport_map,)
    (tm,) = mpi_map_alloc_dmem(
        link_tm_d2, dmem_key_in_list=['d2'], dmem_arg_in_list=['d2'],
        dmem_val_in_list=[d2], dmem_key_out_list=['tm'],
        mpi_pool=mpi_pool)
    # Prepare batch size
    if batch_size is None:
        batch_size = x.shape[0]
    else:
        batch_size = max(
            1 if mpi_pool is None else mpi_pool.nprocs,
            batch_size // d2.dim**2)
    start = 0
    grad_t = np.zeros((x.shape[0], d2.dim))
    abs_exp_gxgt = np.zeros((d2.dim,d2.dim)) if use_fv_hess else None
    while start < x.shape[0]:
        stop = min(x.shape[0], start + batch_size)
        # Compute grad_x and store in distributed memory
        scatter_tuple = (['x'], [x[start:stop,:]])
        (grad_x_tm,) = mpi_map_alloc_dmem(
            'grad_x', scatter_tuple=scatter_tuple, dmem_key_out_list=['grad_x_tm'],
            obj='tm', obj_val=tm, mpi_pool=mpi_pool)
        # Compute first variation and store in memory
        (grad_t_batch,) = mpi_map_alloc_dmem(
            grad_t_kl_divergence, scatter_tuple=scatter_tuple,
            dmem_key_in_list=['d1', 'd2', 'grad_x_tm'],
            dmem_arg_in_list=['d1', 'd2', 'grad_x_tm'],
            dmem_val_in_list=[d1, d2, grad_x_tm],
            dmem_key_out_list=['grad_t'],
            mpi_pool=mpi_pool )
        if mpi_pool is None:
            grad_t[start:stop,:] = grad_t_batch
        else:
            grad_t_list = mpi_pool.get_dmem('grad_t')
            grad_t[start:stop,:] = np.concatenate([gt[0] for gt in grad_t_list], axis=0)
        if use_fv_hess:
            # Compute gradient of first variation
            abs_exp_gxgt += mpi_map(
                grad_x_grad_t_kl_divergence, scatter_tuple=scatter_tuple,
                dmem_key_in_list=['d1', 'd2', 'grad_x_tm', 'grad_t'],
                dmem_arg_in_list=['d1', 'd2', 'grad_x_tm', 'grad_t'],
                dmem_val_in_list=[d1, d2, grad_x_tm, grad_t_batch],
                reduce_obj=AbsExpectationReduce(), reduce_tuple=(['w'], [w[start:stop]]),
                mpi_pool=mpi_pool)
        start = stop
    # Update counters
    if mpi_pool is not None:
        d2_child_list = mpi_pool.get_dmem('d2')
        d2.update_ncalls_tree( d2_child_list[0][0] )
        for (d2_child,) in d2_child_list:
            d2.update_nevals_tree(d2_child)
            d2.update_teval_tree(d2_child)
    # Clear mpi_pool
    if mpi_pool is not None:
        mpi_pool.clear_dmem()
    return grad_t, abs_exp_gxgt
        
def kl_divergence_fv_line_search(
        pi, w, tm_ev, fv_tri_tm_ev, tm_pxd, fv_tri_tm_pxd,
        line_search_params, mpi_pool):

    def objective(x, pi, w, U, pU, mpi_pool):
        # Here x = [T(x)+\delta U(x) | \partial_i T_i(x) + \delta \partial_i U_i(x) ]
        dim = x.shape[1]//2
        TdU = x[:,:dim]
        pTdU = x[:,dim:]
        if np.any(pTdU < 0):
            return np.nan
        lpTdU = np.log(pTdU)
        # Compute pi.log_pdf( T(x)-\delta U(x) )
        scatter_tuple = (['x'], [TdU])
        lpdf = mpi_map('log_pdf', scatter_tuple=scatter_tuple,
                       obj='pi', obj_val=pi, mpi_pool=mpi_pool)
        # Compute log determinant part
        log_det = np.sum(lpTdU, axis=1)
        # Compute output
        out = - np.dot( lpdf + log_det, w )
        return out

    # Distribute pi to the different cores if necessary
    pi_distr = dill.loads( dill.dumps(pi) )
    pi_distr.reset_counters()
    mpi_alloc_dmem(pi=pi, mpi_pool=mpi_pool)

    # Set up line search arguments
    T = tm_ev
    pT = tm_pxd
    U = - fv_tri_tm_ev
    pU = - fv_tri_tm_pxd
    args = (pi, w, U, pU, mpi_pool)
    Tstack = np.hstack( (T, pT) )
    Ustack = np.hstack( (U, pU) )

    # Perform steps of back tracking to find a good delta improving the objective
    # and preserving monotonicity
    maxit = line_search_params.get('maxiter', 20)
    delta = line_search_params.get('delta', 2.)
    isnan = True
    it = 0
    fval0 = objective(Tstack, *args)
    fval = np.inf
    while (isnan or fval > fval0) and it < maxit:
        delta /= 2
        fval = objective(Tstack + delta * Ustack, *args)
        isnan = np.isnan(fval)
        it += 1

    if mpi_pool is not None:
        pi_child_list = mpi_pool.get_dmem('pi')
        pi.update_ncalls_tree( pi_child_list[0][0] )
        for (pi_child,) in pi_child_list:
            pi.update_nevals_tree(pi_child)
            pi.update_teval_tree(pi_child)

    return delta, it < maxit
        
def prune_map(tm, coeffs_weights, coeff_trunc):
    tm = copy.deepcopy(tm)
    # Compute coefficients importance as coeffs * exp_ga_tm
    keep_flags = np.abs(coeffs_weights) > coeff_trunc
    # Run through the components of the map and remove coefficients below threshold
    start = 0
    for d, (avars, comp) in enumerate(zip(tm.active_vars, tm.approx_list)):
        # Constant part
        const_comp = comp.c
        stop = start + const_comp.n_coeffs
        keep_flags_comp = keep_flags[start:stop]
        # Make sure the multi-index (0,0,...,0) is preserved
        zero_idx = const_comp.multi_idxs.index(tuple( [0] * const_comp.dim ))
        keep_flags_comp[zero_idx] = True
        # Remove multi-indices and coefficients
        keep_idxs_comp = list(np.where(keep_flags_comp)[0])
        const_comp.multi_idxs = [ const_comp.multi_idxs[idx] for idx in keep_idxs_comp ]
        const_comp.coeffs = [ const_comp.coeffs[idx] for idx in keep_idxs_comp ]
        start = stop
        # Integrated part
        int_comp = comp.h
        stop = start + int_comp.n_coeffs
        keep_flags_comp = keep_flags[start:stop]
        # Make sure the multi-index (0,0,...,0) is preserved
        zero_idx = int_comp.multi_idxs.index( tuple([0]*int_comp.dim) )
        keep_flags_comp[zero_idx] = True
        # Remove multi-indices and coefficients
        keep_idxs_comp = list(np.where(keep_flags_comp)[0])
        int_comp.multi_idxs = [ int_comp.multi_idxs[idx] for idx in keep_idxs_comp ]
        int_comp.coeffs = [ int_comp.coeffs[idx] for idx in keep_idxs_comp ]
        start = stop
        # Update active variables (union of c and h) and dimensions of c, h, comp
        const_midxs_mat = np.asarray( const_comp.multi_idxs )
        int_midxs_mat = np.asarray( int_comp.multi_idxs )
        keep_idxs = [ i for i in range(comp.dim-1) \
                      if np.any( const_midxs_mat[:,i] != 0 ) \
                      or np.any( int_midxs_mat[:,i] != 0 ) ] + [comp.dim-1]
        const_midxs_mat = const_midxs_mat[:,keep_idxs]
        int_midxs_mat = int_midxs_mat[:,keep_idxs]
        dim = const_midxs_mat.shape[1]
        tm.active_vars[d] = [ avars[idx] for idx in keep_idxs ]
        comp.dim = dim
        const_comp.multi_idxs = mat_idxs_to_list_idxs(const_midxs_mat)
        const_comp.basis_list = [ const_comp.basis_list[idx] for idx in keep_idxs ]
        const_comp.dim = dim
        int_comp.multi_idxs = mat_idxs_to_list_idxs(int_midxs_mat)
        int_comp.basis_list = [ int_comp.basis_list[idx] for idx in keep_idxs ]
        int_comp.dim = dim
    return tm
        
def improved_candidate_map(transport_map, fv_map):
    active_vars = []
    approx_list = []
    for d, (tm_avars, tm_comp,
            fv_avars, fv_comp) in enumerate(zip(
                transport_map.active_vars, transport_map.approx_list,
                fv_map.active_vars, fv_map.approx_list)):
        tm_full_c_blist = tm_comp.c.full_basis_list
        tm_full_h_blist = tm_comp.h.full_basis_list
        # Transform multi-indices into matrices
        tmc_midxs_mat = np.asarray(tm_comp.c.multi_idxs)
        tmh_midxs_mat = np.asarray(tm_comp.h.multi_idxs)
        fv_midxs_mat = np.asarray(fv_comp.multi_idxs)
        # Find active variables to be added to the transport map component
        add_var = [var for var in fv_avars if not var in tm_avars]
        # Add zero columns to the multi-indices of tm_comp
        nmidxs_c = tmc_midxs_mat.shape[0]
        nmidxs_h = tmh_midxs_mat.shape[0]
        for var in add_var:
            ivar = fv_avars.index(var)
            tmc_midxs_mat = np.hstack(
                (tmc_midxs_mat[:,:ivar],
                 np.zeros((nmidxs_c,1), dtype=int),
                 tmc_midxs_mat[:,ivar:]) )
            tmh_midxs_mat = np.hstack(
                (tmh_midxs_mat[:,:ivar],
                 np.zeros((nmidxs_h,1), dtype=int),
                 tmh_midxs_mat[:,ivar:]) )
        # Split fv_comp multi-indices into constant and integrated parts
        c_rows = list(np.where(fv_midxs_mat[:,-1] == 0)[0])
        h_rows = list(set(range(fv_midxs_mat.shape[0])).difference(set(c_rows)))
        fvc_midxs_mat = fv_midxs_mat[c_rows,:]
        fvh_midxs_mat = fv_midxs_mat[h_rows,:]
        # Adjust multi-index for the integrated part
        fvh_midxs_mat[:,-1] -= 1
        # Transform multi-indices into lists
        tmc_midxs = [ tuple(midx) for midx in list(tmc_midxs_mat) ]
        tmh_midxs = [ tuple(midx) for midx in list(tmh_midxs_mat) ]
        fvc_midxs = [ tuple(midx) for midx in list(fvc_midxs_mat) ]
        fvh_midxs = [ tuple(midx) for midx in list(fvh_midxs_mat) ]
        # Enrich transport map component
        add_c_midxs = list( set(fvc_midxs) - set(tmc_midxs) )
        add_h_midxs = list( set(fvh_midxs) - set(tmh_midxs) )
        tmc_midxs += add_c_midxs
        tmh_midxs += add_h_midxs
        # Build basis (using the full basis set provided by the transport map)
        c_basis = [ tm_full_c_blist[a] for a in fv_avars ]
        h_basis = [ tm_full_h_blist[a] for a in fv_avars ]
        # Build constant and integrated linear span functions
        c = LinearSpanApproximation(
            c_basis, spantype='midx', multi_idxs=tmc_midxs,
            full_basis_list=tm_full_c_blist)
        h = LinearSpanApproximation(
            h_basis, spantype='midx', multi_idxs=tmh_midxs,
            full_basis_list=tm_full_h_blist)
        # Set coefficients
        c.coeffs = np.hstack((tm_comp.c.coeffs, np.zeros(len(add_c_midxs))))
        h.coeffs = np.hstack((tm_comp.h.coeffs, np.zeros(len(add_h_midxs))))
        # Assemble component
        comp = type(tm_comp)(c, h)
        # Append to list of components and active variables
        approx_list.append(comp)
        active_vars.append(fv_avars[:])
    new_map = type(transport_map)(
        active_vars, approx_list,
        full_c_basis_list=transport_map.full_c_basis_list,
        full_h_basis_list=transport_map.full_h_basis_list)
    return new_map
        
def first_variation_candidate_triangular_map(
        transport_map, sensitivities, avar_trunc):
    r""" Construct the candidate map to be used in the regression of the first variation.

    It takes the multi-indices in ``transport_map`` and increases them by one,
    adding also active variables if needed.
    The active variables to add are detected using the second moment of the
    first variation, if available.
    """
    active_vars = []
    midxs_list = []
    if sensitivities is not None:
        scaled_sensitivities = sensitivities / np.max(sensitivities)
    else:
        scaled_sensitivities = None
    for d, (tm_comp, tm_comp_avar) in enumerate(zip(
            transport_map.approx_list, transport_map.active_vars)):
        # Update active variables using second order information
        if scaled_sensitivities is not None:
            # tmp = np.abs(exp_gxgt[d,:d+1])
            # scaled_avar_diag = tmp / np.max(tmp)
            # fv_avar = list(np.where(scaled_avar_diag > avar_trunc)[0])
            fv_avar = list(np.where(scaled_sensitivities[d,:d] > avar_trunc)[0])
            add_avar = [ var for var in fv_avar if not var in tm_comp_avar ]
        else:
            add_avar = []
        avar = sorted( tm_comp_avar + add_avar )
        # Adjust multi-index of the exponential part to map to the linear span approx
        h_midxs_mat = np.asarray(tm_comp.h.multi_idxs)
        h_midxs_mat[:,-1] += 1 
        h_midxs = mat_idxs_to_list_idxs(h_midxs_mat)
        # Merge constant and integrated multi-indices
        tm_approx_midxs = tm_comp.c.multi_idxs + h_midxs
        # Transform multi-indices into matrix
        tm_approx_midxs_mat = np.asarray(tm_approx_midxs)
        # Add zero columns to the multi-indices
        for var in add_avar:
            ivar = avar.index(var)
            nmidxs = tm_approx_midxs_mat.shape[0]
            tm_approx_midxs_mat = np.hstack( (tm_approx_midxs_mat[:,:ivar],
                                              np.zeros((nmidxs,1), dtype=int),
                                              tm_approx_midxs_mat[:,ivar:]) )
        # Extract maximum order per direction
        max_ord_vec = np.max(tm_approx_midxs_mat, axis=0)
        max_ord = np.max(np.sum(tm_approx_midxs_mat, axis=1))    
        # Generate new multi-index (GREAT BOTTLENECK)
        max_ord_list = list( max_ord_vec + 1 )
        max_ord += 1
        midxs = generate_total_order_midxs(max_ord_list) # TODO: cython implementation
        # Update
        active_vars.append(avar)
        midxs_list.append(midxs)
    fv_approx = Default_LinearSpanTriangularTransportMap(
        transport_map.dim, midxs_list, active_vars)
    return fv_approx

def mat_idxs_to_list_idxs(mat_idxs):
    return [tuple(idxs) for idxs in list(mat_idxs)]


def map_structure_str(tm, indent, verbosity=0):
    out = indent + "Number of degrees of freedom: %d\n" % tm.n_coeffs
    if verbosity > 0:
        for d, (comp, avars) in enumerate(zip(tm.approx_list, tm.active_vars)):
            out += indent + "Component %3d: Active variables: %s\n" % (d, str(avars))
            out += indent + "   Const part - midxs: %s\n" % (comp.c.multi_idxs)
            if verbosity > 1:
                out += indent + "   Const part - coeffs: %s\n" % (comp.c.coeffs)
            out += indent + "   Integ part - midxs: %s\n" % (comp.h.multi_idxs)
            if verbosity > 1:
                out += indent + "   Integ part - coeffs: %s\n" % (comp.h.coeffs)
    return out

def map_sparsity_str(tm, indent, verbosity=0):
    navar = sum([len(avars) for avars in tm.active_vars])
    totvar = (tm.dim+1)*tm.dim / 2
    out = indent + "Map sparsity: %d/%d (%.4f%%)\n" % (
        navar, totvar, float(navar)/float(totvar)*100)
    if verbosity > 0:
        for d, avars in enumerate(tm.active_vars):
            str_list = [' '] * tm.dim
            for var in avars:
                str_list[var] = 'x'
            out += indent + '   |' + ''.join(str_list) + '|' + '\n'
    return out

def is_equal_map(tm1, tm2):
    match = True
    for d, (c1, a1, c2, a2) in enumerate(zip(
            tm1.approx_list, tm1.active_vars, tm2.approx_list, tm2.active_vars)):
        match = set(a1) == set(a2)
        if not match:
            break
        match = set(c1.c.multi_idxs) == set(c2.c.multi_idxs)
        if not match:
            break
        match = set(c1.h.multi_idxs) == set(c2.h.multi_idxs)
        if not match:
            break
    return match
