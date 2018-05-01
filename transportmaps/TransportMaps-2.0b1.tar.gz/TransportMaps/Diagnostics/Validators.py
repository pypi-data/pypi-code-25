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

import numpy as np
import numpy.linalg as npla
import numpy.random as npr
import scipy.stats as stats
import scipy.optimize as sciopt
import scipy.linalg as scila

from TransportMaps import mpi_map, distributed_sampling
from TransportMaps.ObjectBase import TMO
from TransportMaps.Distributions.TransportMapDistributions import \
    PullBackTransportMapDistribution

__all__ = ['KLMinimizationValidator',
           'SampleAverageApproximationKLMinimizationValidator',
           'GradientChi2KLMinimizationValidator',
           'GradientStabilityKLMinimizationValidator']

class KLMinimizationValidator(TMO):
    def __init__(
            self, eps_sp, cost_function, max_cost, eps_sp_rel=0,
            max_nsamps=np.inf, stop_on_fcast=False):
        super(KLMinimizationValidator, self).__init__()
        self.eps_sp_abs = eps_sp
        self.eps_sp_rel = eps_sp_rel
        self.cost_function = cost_function
        self.max_cost = max_cost
        self.max_nsamps = max_nsamps
        self.stop_on_fcast = stop_on_fcast

    def solve_to_tolerance(
            self, transport_map, base_distribution, target_distribution,
            solve_params):
        log = {}
        max_nsamps_flag = False
        cost = self.cost_function(
            ncalls=getattr(target_distribution, 'ncalls', {}),
            nevals=getattr(target_distribution, 'nevals', {}),
            teval=getattr(target_distribution, 'teval', {}))
        cost_flag = cost > self.max_cost
        fcast_cost = 0.
        fcast_cost_flag = False
        err = np.inf
        err_mag = 0
        target_err = err_mag * self.eps_sp_rel + self.eps_sp_abs
        prune_params = None

        pull_tar = PullBackTransportMapDistribution(
            transport_map, target_distribution)
        ncalls_x_solve = getattr(target_distribution, 'ncalls', {}).copy()
        lst_ncalls = getattr(target_distribution, 'ncalls', {}).copy()

        it = 1
        while err > target_err and not cost_flag:
            if it > 1:
                # Compute refinement and forecast cost flag
                solve_params['qparams'], nsamps = self.refinement(
                    base_distribution, pull_tar,
                    qtype=solve_params['qtype'], qparams=solve_params['qparams'],
                    err_mag=err_mag, ref_params=ref_params)
                self.logger.info("Refinement - nsamps: %d" % nsamps)
                if nsamps >= self.max_nsamps:
                    max_nsamps_flag = True
                    self.logger.warning("Maximum number of samples reached.")
                    break
                if self.stop_on_fcast:
                    fcast_cost = self.cost_function(
                        ncalls=target_distribution.ncalls,
                        nevals=target_distribution.nevals,
                        teval=target_distribution.teval,
                        ncalls_x_solve=ncalls_x_solve, new_nx=nsamps)
                    fcast_cost_flag = fcast_cost > self.max_cost
                    if fcast_cost_flag: # Stop
                        self.logger.warning("Predicted cost exceeds maximum cost allowed.")
                        break
                solve_params['x0'] = transport_map.coeffs # Warm start
            # Solve
            log = transport_map.minimize_kl_divergence(
                base_distribution, pull_tar, **solve_params)
            if not log['success']:
                cost = self.cost_function(
                    ncalls=target_distribution.ncalls,
                    nevals=target_distribution.nevals,
                    teval=target_distribution.teval)
                break
            # Estimate error and compute cost flag
            solve_params['x0'] = transport_map.coeffs # Warm start
            err, err_mag, ref_params, prune_params = self.error_estimation(
                base_distribution, pull_tar, solve_params, full_output=True)
            target_err = err_mag * self.eps_sp_rel + self.eps_sp_abs
            ncalls_x_solve = {
                key: value - lst_ncalls.get(key,0)
                for key, value in pull_tar.ncalls.items()}
            lst_ncalls = pull_tar.ncalls.copy()
            cost = self.cost_function(
                ncalls=target_distribution.ncalls,
                nevals=target_distribution.nevals,
                teval=target_distribution.teval)
            cost_flag = cost > self.max_cost
            self.print_info(err, target_err, cost, solve_params, ref_params, prune_params)
            it += 1

        log['validator_max_nsamps_exceeded'] = max_nsamps_flag
        log['validator_cost'] = cost
        log['validator_cost_exceeded'] = cost_flag
        log['validator_fcast_cost'] = fcast_cost
        log['validator_fcast_cost_exceeded'] = fcast_cost_flag
        log['validator_error'] = err
        log['validator_prune_params'] = prune_params
        log['validator_target_error'] = target_err
        return log

    def print_info(self, err, target_err, cost, solve_params, ref_params, prune_params):
        self.logger.info(
            "nsamps: %d - " % solve_params['qparams'] + \
            "err: %.3e (target: %.3e)" % (err, target_err) + \
            "- cost: %.2e" % cost)
        
    def error_estimation(self, base_distribution, pull_tar, solve_params):
        raise NotImplementedError("To be implemented in subclasses")

    def refinement(self, base_distribution, pull_tar,
                   qtype, qparams, ref_params):
        r"""
        Returns:
          (:class:`tuple`) -- containing the new ``qparams`` and the
            number of points corresponding to it.
        """
        raise NotImplementedError("To be implemented in subclasses")

class SampleAverageApproximationKLMinimizationValidator(KLMinimizationValidator):
    def __init__(self, eps_sp_rel, eps_sp_abs, cost_function, max_cost,
                 max_nsamps=np.inf, stop_on_fcast=False,
                 upper_mult=10, lower_n=2, alpha=0.05,
                 lmb_def=2, lmb_max=10):
        if upper_mult < 1:
            raise AttributeError("The upper_mult argument must be a float >= 1")
        if lower_n < 2:
            raise AttributeError("The lower_n argument must be an integer >= 2")
        self.upper_mult = upper_mult
        self.lower_n = lower_n
        self.alpha = alpha
        self.lmb_def = lmb_def
        self.lmb_max = lmb_max
        super(SampleAverageApproximationKLMinimizationValidator,
              self).__init__(
                  eps_sp_abs, cost_function, max_cost, eps_sp_rel=eps_sp_rel,
                  max_nsamps=max_nsamps, stop_on_fcast=stop_on_fcast)

    def print_info(self, err, target_err, cost, solve_params, ref_params, prune_params):
        self.logger.info(
            "nsamps: %d " % solve_params['qparams'] + \
            "- err: %.3e [L: %.3e, U:%.3e] (target: %.3e) " % (
                err, ref_params['lower_interval'],
                ref_params['upper_interval'], target_err) + \
            "- cost: %.2e" % cost)
        
    def error_estimation(
            self, base_distribution, pull_tar, solve_params, full_output=False):
        if solve_params['qtype'] != 0:
            raise AttributeError(
                "The Sample Average Approximation validator is defined only for " + \
                "Monte Carlo quadrature rules")
        tm = pull_tar.transport_map
        # Compute upper bound (distributed sampling)
        upper_nsamps = int(np.ceil(self.upper_mult * solve_params['qparams']))
        (x, w) = distributed_sampling(
            base_distribution, 0, upper_nsamps, mpi_pool=solve_params.get('mpi_pool'))
        v2 = - mpi_map(
            "log_pdf", obj=pull_tar,
            dmem_key_in_list=['x'],
            dmem_arg_in_list=['x'],
            dmem_val_in_list=[x],
            mpi_pool=solve_params.get('mpi_pool'))
        if solve_params['regularization'] is not None:
            if solve_params['regularization']['type'] == 'L2':
                v2 += solve_params['regularization']['alpha'] * \
                      npla.norm(tm.coeffs - tm.get_identity_coeffs(), 2)**2.
        upper_mean = np.sum( v2 ) / float(upper_nsamps)
        upper_var = np.sum( (v2 - upper_mean)**2 ) / float(upper_nsamps-1)
        upper_interval = stats.t.ppf(1-self.alpha, upper_nsamps) * \
                         np.sqrt(upper_var/float(upper_nsamps))
        upper_bound = upper_mean + upper_interval
        # Compute lower bound
        res_coeffs = pull_tar.coeffs[:]
        lower_nsamps = self.lower_n
        v2 = np.zeros(lower_nsamps)
        coeffs = np.zeros((lower_nsamps, tm.n_coeffs))
        for i in range(lower_nsamps):
            log = tm.minimize_kl_divergence(
                base_distribution, pull_tar, **solve_params)
            v2[i] = log['fval']
            coeffs[i,:] = tm.coeffs
        lower_mean = np.sum(v2) / float(lower_nsamps)
        lower_var = np.sum((v2 - lower_mean)**2) / float(lower_nsamps-1)
        lower_interval = stats.t.ppf(1-self.alpha, lower_nsamps) * \
                         np.sqrt(lower_var/float(lower_nsamps))
        lower_bound = lower_mean - lower_interval
        pull_tar.coeffs = res_coeffs # Restore coefficients
        # Error as the gap between the bounds
        err = max(0., upper_bound - lower_bound)
        if full_output:
            # Refinement parameters
            ref_params = {
                'upper_nsamps': upper_nsamps,
                'upper_mean': upper_mean,
                'upper_var': upper_var,
                'upper_interval': upper_interval,
                'lower_nsamps': lower_nsamps,
                'lower_mean': lower_mean,
                'lower_var': lower_var,
                'lower_interval': lower_interval
            }
            # Pruning parameter as 1/stand.dev. of coefficients scaled to (0,1)
            std_coeffs = np.std(coeffs, axis=0)
            prune_params = (1/std_coeffs)/max(1/std_coeffs)
            return err, upper_mean, ref_params, prune_params
        else:
            return err

    def refinement(self, base_distribution, pull_tar,
                   qtype, qparams, err_mag, ref_params):
        if qtype != 0:
            raise AttributeError(
                "The Sample Average Approximation validator is defined only for " + \
                "Monte Carlo quadrature rules")
        X = (self.eps_sp_abs + self.eps_sp_rel * err_mag) - \
            (ref_params['upper_mean'] - ref_params['lower_mean']) - \
            stats.t.ppf(1-self.alpha, ref_params['upper_nsamps']) * \
            np.sqrt(ref_params['upper_var']/ref_params['upper_nsamps'])
        if X > 0:
            def f(m, alpha, X, lv):
                return stats.t.ppf(1-alpha, m) / m * np.sqrt(lv) - X
            if np.sign(
                    f(ref_params['lower_nsamps'], self.alpha,
                      X, ref_params['lower_var']) ) * \
                np.sign(
                    f(self.lmb_max, self.alpha,
                      X, ref_params['lower_var']) ) == -1:
                m = sciopt.bisect(
                    f, ref_params['lower_nsamps'], self.lmb_max,
                    args=(self.alpha, X, ref_params['lower_var']))
                q = int(np.ceil( m/ref_params['lower_nsamps'] * qparams ))
            else:
                q = int( np.ceil(self.lmb_def * qparams) )
        else:
            q = int( np.ceil(self.lmb_def * qparams) )
        q = min(q, self.max_nsamps)
        return q, q

class GradientChi2KLMinimizationValidator(KLMinimizationValidator):
    def __init__(self, eps_sp, cost_function, max_cost,
                 max_nsamps=np.inf, stop_on_fcast=False,
                 n_grad_samps=10, n_bootstrap=None,
                 alpha=0.95, lmb_def=2, lmb_max=10,
                 fungrad=False):
        self.n_grad_samps = n_grad_samps
        self.n_bootstrap = n_bootstrap
        self.alpha = alpha
        self.lmb_def = lmb_def
        self.lmb_max = lmb_max
        self.fungrad = fungrad
        super(GradientChi2KLMinimizationValidator,
              self).__init__(eps_sp, cost_function, max_cost, max_nsamps, stop_on_fcast)
        
    def error_estimation(
            self, base_distribution, pull_tar, solve_params, full_output=False):
        if solve_params['qtype'] != 0:
            raise AttributeError(
                "The Gradient Stability validator is defined only for " + \
                "Monte Carlo quadrature rules")
        tm = pull_tar.transport_map
        # Compute mean and variance of the gradient
        nsamps = int(np.ceil( self.n_grad_samps * solve_params['qparams'] ))
        x, w = base_distribution.quadrature(
            qtype=solve_params['qtype'], qparams=nsamps)
        scatter_tuple = (['x'], [x])
        if not self.fungrad:
            grad = - mpi_map(
                "grad_a_log_pdf", obj=pull_tar, scatter_tuple=scatter_tuple,
                mpi_pool=solve_params.get('mpi_pool'))
        else:
            _, grad = - mpi_map(
                "tuple_grad_a_log_pdf", obj=pull_tar, scatter_tuple=scatter_tuple,
                mpi_pool=solve_params.get('mpi_pool'))
        if solve_params['regularization'] is not None:
            if solve_params['regularization']['type'] == 'L2':
                grad += solve_params['regularization']['alpha'] * 2. * \
                        (tm.coeffs - tm.get_identity_coeffs())
        # Use randomized resampling to avoid being forced to use n_grad_samps > tm.n_coeffs
        if self.n_bootstrap is None:
            avg_grads = np.mean( grad.reshape((
                solve_params['qparams'], self.n_grad_samps, tm.n_coeffs)), axis=0 )
        else:
            avg_grads = np.zeros((self.n_bootstrap, tm.n_coeffs))
            for i in range(self.n_bootstrap):
                idxs = npr.choice(nsamps, size=solve_params['qparams'], replace=True)
                avg_grads[i,:] = np.mean( grad[idxs,:], axis=0 )
        mean = np.mean(avg_grads, axis=0)
        cntr_avg_grads = avg_grads - mean
        cov = np.dot(cntr_avg_grads.T, cntr_avg_grads) / float(solve_params['qparams']-1)
        L = scila.cholesky(cov, lower=True)
        cstar = stats.chi2(tm.n_coeffs).ppf(self.alpha)
        # Solve maximization problem
        A = - cstar/solve_params['qparams'] * np.dot(L.T,L)
        b = - 2. * np.sqrt(cstar/solve_params['qparams']) * np.dot(mean, L)
        c = - np.dot(mean, mean)
        def f(x, A, b, c):
            return np.dot(x,np.dot(A,x)) + np.dot(b, x) + c
        def jac(x, A, b, c):
            return 2. * np.dot(A,x) + b
        def c1(x):
            return 1 - np.dot(x,x)
        def c1jac(x):
            return - 2 * x
        cons = ({'type': 'ineq', 'fun': c1, 'jac': c1jac})
        res = sciopt.minimize(
            f, np.zeros(tm.n_coeffs), method='SLSQP', jac=jac, 
            args=(A, b, c), constraints=cons, tol=1e-12)
        xstar = res['x']
        # Compute err as sqrt(f(x))
        err = np.sqrt(- f(xstar, A, b, c))
        if full_output:
            # Refinement parameters
            ref_params = {
                'mean':mean,
                'L': L,
                'cstar': cstar,
                'xstar': xstar
            }
            # Prune parameter as 1/variance of directional gradient
            var_coeffs = np.diag(cov)
            prune_params = (1/var_coeffs)/max(1/var_coeffs)
            return err, ref_params, prune_params
        else:
            return err

    def refinement(self, base_distribution, pull_tar,
                   qtype, qparams, ref_params):
        if qtype != 0:
            raise AttributeError(
                "The Gradient Stability validator is defined only for " + \
                "Monte Carlo quadrature rules")
        # Load parameters
        mu = ref_params['mean']
        L = ref_params['L']
        cstar = ref_params['cstar']
        xstar = ref_params['xstar']
        # Compute refinement
        a = np.dot(mu,mu) - self.eps_sp**2
        if a <= 0:
            Lx = np.dot(L, xstar)
            b = 2. * np.sqrt(cstar) * np.dot(mu, np.dot(L, xstar))
            c = cstar * np.dot(Lx.T, Lx)
            z = (-b + np.sqrt(b**2-4*a*c))/ 2. / a
            q = min( int(np.ceil(z**2)),
                     self.lmb_max * qparams )
        else:
            q = int( np.ceil(self.lmb_def * qparams) )
        return q, q
        
class GradientStabilityKLMinimizationValidator(KLMinimizationValidator):
    def __init__(self, eps_sp, cost_function, max_cost,
                 max_nsamps=np.inf, stop_on_fcast=False,
                 n_grad_samps=10, n_gap_resampling=10,
                 beta=0.95, gamma=0.05, lmb_def=2, lmb_max=10,
                 fungrad=False):
        self.n_grad_samps = n_grad_samps
        self.n_gap_resampling = n_gap_resampling
        self.beta = beta
        self.gamma = gamma
        self.lmb_def = lmb_def
        self.lmb_max = lmb_max
        self.fungrad = fungrad
        super(GradientStabilityKLMinimizationValidator,
              self).__init__(eps_sp, cost_function, max_cost, max_nsamps, stop_on_fcast)

    def _cv(self, N, n, b, g):
        n = self.n_grad_samps
        b = self.beta
        g = self.gamma
        return (n-1) * stats.chi2(N, loc=float(N)/float(n)).ppf(b) / \
            stats.chi2(n-N).ppf(1-g)
        
    def error_estimation(
            self, base_distribution, pull_tar, solve_params, full_output=False):
        if solve_params['qtype'] != 0:
            raise AttributeError(
                "The Gradient Stability validator is defined only for " + \
                "Monte Carlo quadrature rules")
        tm = pull_tar.transport_map
        # Compute mean and variance of the gradient
        nsamps = int(np.ceil( self.n_grad_samps * solve_params['qparams'] ))
        x, w = base_distribution.quadrature(
            qtype=solve_params['qtype'], qparams=nsamps)
        scatter_tuple = (['x'], [x])
        if not self.fungrad:
            grad = - mpi_map(
                "grad_a_log_pdf", obj=pull_tar, scatter_tuple=scatter_tuple,
                mpi_pool=solve_params.get('mpi_pool'))
        else:
            _, grad = - mpi_map(
                "tuple_grad_a_log_pdf", obj=pull_tar, scatter_tuple=scatter_tuple,
                mpi_pool=solve_params.get('mpi_pool'))
        if solve_params['regularization'] is not None:
            if solve_params['regularization']['type'] == 'L2':
                grad += solve_params['regularization']['alpha'] * 2. * \
                        (tm.coeffs - tm.get_identity_coeffs())
        # Use randomized resampling to avoid being forced to use n_grad_samps > tm.n_coeffs
        n = tm.n_coeffs + self.n_gap_resampling
        avg_grads = np.zeros((n, tm.n_coeffs))
        for i in range(n):
            idxs = npr.choice(nsamps, size=solve_params['qparams'], replace=False)
            avg_grads[i,:] = np.mean( grad[idxs,:], axis=0 )
        mean = np.mean(avg_grads, axis=0)
        cntr_avg_grads = avg_grads - mean
        cov = np.dot(cntr_avg_grads.T, cntr_avg_grads) / float(n-1)
        L = scila.cholesky(cov, lower=True)
        cstar = self._cv(tm.n_coeffs, n, self.beta, self.gamma)
        # Solve maximization problem
        A = - cstar/solve_params['qparams'] * np.dot(L.T,L)
        b = - 2. * np.sqrt(cstar/solve_params['qparams']) * np.dot(mean, L)
        c = - np.dot(mean, mean)
        def f(x, A, b, c):
            return np.dot(x,np.dot(A,x)) + np.dot(b, x) + c
        def jac(x, A, b, c):
            return 2. * np.dot(A,x) + b
        def c1(x):
            return 1 - np.dot(x,x)
        def c1jac(x):
            return - 2 * x
        cons = ({'type': 'ineq', 'fun': c1, 'jac': c1jac})
        res = sciopt.minimize(
            f, np.zeros(tm.n_coeffs), method='SLSQP', jac=jac, 
            args=(A, b, c), constraints=cons, tol=1e-12)
        xstar = res['x']
        # Compute err as sqrt(f(x))
        err = np.sqrt(f(xstar, A, b, c))
        if full_output:
            # Refinement parameters
            ref_params = {
                'mean':mean,
                'L': L,
                'cstar': cstar,
                'xstar': xstar
            }
            # Compute prune parameters as 1/ variance of gradient
            var_coeffs = np.diag(cov)
            prune_params = (1/var_coeffs)/max(1/var_coeffs)
            return err, ref_params, prune_params
        else:
            return err

    def refinement(self, base_distribution, pull_tar,
                   qtype, qparams, ref_params):
        if qtype != 0:
            raise AttributeError(
                "The Gradient Stability validator is defined only for " + \
                "Monte Carlo quadrature rules")
        # Load parameters
        mu = ref_params['mean']
        L = ref_params['L']
        cstar = ref_params['cstar']
        xstar = ref_params['xstar']
        # Compute refinement
        a = np.dot(mu,mu) - self.eps_sp**2
        if a <= 0:
            Lx = np.dot(L, xstar)
            b = 2. * np.sqrt(cstar) * np.dot(mu, np.dot(L, xstar))
            c = cstar * np.dot(Lx.T, Lx)
            z = (-b + np.sqrt(b**2-4*a*c))/ 2. / a
            q = int(np.ceil(z**2))
        else:
            q = int( np.ceil(self.lmb_def * qparams) )
        return q, q

