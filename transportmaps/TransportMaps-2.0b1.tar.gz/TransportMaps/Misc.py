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

import sys
import logging
import time
from functools import wraps
import numpy as np
from TransportMaps.External import MPI_SUPPORT

__all__ = ['LOG_LEVEL', 'logger', 'deprecate', 'setLogLevel', 'counted',
  	 	   'get_mpi_pool', 'mpi_eval',
           'mpi_map', 'mpi_map_alloc_dmem', 'mpi_alloc_dmem',
           'SumChunkReduce', 'TupleSumChunkReduce',
           'TensorDotReduce', 'ExpectationReduce',
           'AbsExpectationReduce', 'TupleExpectationReduce',
           'distributed_sampling',
		   'generate_total_order_midxs',
           'total_time_cost_function',
           'cached', 'cached_tuple', 'get_sub_cache',
           'taylor_test']

def process_time():
    if sys.version_info >= (3, 3):
        return time.process_time()
    else:
        return time.clock()

####### LOGGING #########
LOG_LEVEL = logging.getLogger().getEffectiveLevel()

logger = logging.getLogger('TM.TransportMaps')
logger.propagate = False
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

def deprecate(name, version, msg):
    def deprecate_decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger.warning("%s DEPRECATED since v%s. %s" % (name, version, msg))
            return f(*args, **kwargs)
        return wrapped
    return deprecate_decorator

def setLogLevel(level):
    r""" Set the log level for all existing and new objects related to the TransportMaps module

    Args:
      level (int): logging level

    .. see:: the :module:`logging` module.
    """
    import TransportMaps as TM
    TM.LOG_LEVEL = level
    for lname, logger in logging.Logger.manager.loggerDict.items():
        if "TM." in lname:
            logger.setLevel(level)

def counted(f): # Decorator used to count function calls
    @wraps(f)
    def wrapped(slf, *args, **kwargs):
        try:
            x = args[0]
        except IndexError:
            x = kwargs['x']
        try:
            slf.ncalls[f.__name__] += 1
            slf.nevals[f.__name__] += x.shape[0]
        except AttributeError:
            slf.ncalls = {}
            slf.nevals = {}
            slf.ncalls[f.__name__] = 1
            slf.nevals[f.__name__] = x.shape[0]
        except KeyError:
            slf.ncalls[f.__name__] = 1
            slf.nevals[f.__name__] = x.shape[0]
        start = process_time()
        out = f(slf, *args, **kwargs)
        stop = process_time()
        try:
            slf.teval[f.__name__] += (stop-start)
        except AttributeError:
            slf.teval = {}
            slf.teval[f.__name__] = (stop-start)
        except KeyError:
            slf.teval[f.__name__] = (stop-start)
        return out
    return wrapped

            
####### MPI ##########
def get_mpi_pool():
    r""" Get a pool of ``n`` processors
    
    Returns:
      (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`) -- pool of processors

    Usage example::
    
        import numpy as np
        import numpy.random as npr
        from TransportMaps import get_mpi_pool, mpi_map

        class Operator(object):
            def __init__(self, a):
                self.a = a
            def sum(self, x, n=1):
                out = x
                for i in range(n):
                    out += self.a
                return out

        op = Operator(2.)
        x = npr.randn(100,5)
        n = 2

        pool = get_mpi_pool()
        pool.start(3)
        try:
            xsum = mpi_map("sum", op, x, (n,), mpi_pool=pool)
        finally:
            pool.stop()
    """
    if MPI_SUPPORT:
        import mpi_map as mpi_map_mod
        return mpi_map_mod.MPI_Pool_v2()
    else:
        raise RuntimeError("MPI is not supported")

@deprecate('mpi_eval', 'v2.0', 'mpi_map')
def mpi_eval(f, scatter_tuple=None, bcast_tuple=None,
             dmem_key_in_list=None, dmem_arg_in_list=None, dmem_val_in_list=None,
             dmem_key_out_list=None,
             obj=None, reduce_obj=None, reduce_tuple=None, import_set=None,
             mpi_pool=None, splitted=False, concatenate=True):
    r""" Interface for the parallel evaluation of a generic function on points ``x``

    Args:
      f (:class:`object` or :class:`str`): function or string identifying the
        function in object ``obj``
      scatter_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes.
      bcast_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be broadcasted to the processes.
      dmem_key_in_list (list): list of string containing the keys
        to be fetched (or created with default ``None`` if missing) from the
        distributed memory and provided as input to ``f``.
      dmem_val_in_list (list): list of objects corresponding to the keys defined
        in ``dmem_key_in_list``, used in case we are not executing in parallel
      dmem_key_out_list (list): list of keys to be assigned to the outputs
        beside the first one
      obj (object): object where the function ``f_name`` is defined
      reduce_obj (object): object :class:`ReduceObject` defining the reduce
        method to be applied (if any)   
      reduce_tuple (object): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes to be used by ``reduce_obj``
      import_set (set): list of couples ``(module_name,as_field)`` to be imported
        as ``import module_name as as_field``
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processors
      splitted (bool): whether the scattering input is already splitted or not
      concatenate (bool): whether to concatenate the output (the output of ``f``
        must be a :class:`numpy.ndarray<numpy.ndarray>` object
    """
    if dmem_key_out_list is None:
        return mpi_map(f=f, scatter_tuple=scatter_tuple, bcast_tuple=bcast_tuple,
                       dmem_key_in_list=dmem_key_in_list,
                       dmem_arg_in_list=dmem_arg_in_list,
                       dmem_val_in_list=dmem_val_in_list,
                       obj=obj, reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
                       import_set=import_set, mpi_pool=mpi_pool,
                       splitted=splitted, concatenate=concatenate)
    else:
        out = mpi_map_alloc_dmem(
            f=f, scatter_tuple=scatter_tuple, bcast_tuple=bcast_tuple,
            dmem_key_in_list=dmem_key_in_list,
            dmem_arg_in_list=dmem_arg_in_list,
            dmem_val_in_list=dmem_val_in_list,
            dmem_key_out_list=dmem_key_out_list,
            obj=obj, reduce_obj=reduce_obj, reduce_tuple=reduce_tuple,
            import_set=import_set, mpi_pool=mpi_pool,
            splitted=splitted, concatenate=concatenate)
        return (None,) + out
    
def mpi_map(f, scatter_tuple=None, bcast_tuple=None,
            dmem_key_in_list=None, dmem_arg_in_list=None, dmem_val_in_list=None,
            obj=None, obj_val=None,
            reduce_obj=None, reduce_tuple=None, 
            mpi_pool=None, splitted=False, concatenate=True):
    r""" Interface for the parallel evaluation of a generic function on points ``x``

    Args:
      f (:class:`object` or :class:`str`): function or string identifying the
        function in object ``obj``
      scatter_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes.
      bcast_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be broadcasted to the processes.
      dmem_key_in_list (list): list of string containing the keys
        to be fetched (or created with default ``None`` if missing) from the
        distributed memory and provided as input to ``f``.
      dmem_val_in_list (list): list of objects corresponding to the keys defined
        in ``dmem_key_in_list``, used in case we are not executing in parallel
      obj (object or str): object where the function ``f_name`` is defined
      obj_val (object): object to be used in case not executing in parallel and
        ``obj`` is a string
      reduce_obj (object): object :class:`ReduceObject` defining the reduce
        method to be applied (if any)   
      reduce_tuple (object): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes to be used by ``reduce_obj``
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processors
      splitted (bool): whether the scattering input is already splitted or not
      concatenate (bool): whether to concatenate the output (the output of ``f``
        must be a :class:`numpy.ndarray<numpy.ndarray>` object
    """
    # Init un-set arguments
    if scatter_tuple is None:
        scatter_tuple = ([],[])
    if bcast_tuple is None:
        bcast_tuple = ([],[])
    if dmem_key_in_list is None:
        dmem_key_in_list = []
    if dmem_arg_in_list is None:
        dmem_arg_in_list = []
    if dmem_val_in_list is None:
        dmem_val_in_list = []
    if reduce_tuple is None:
        reduce_tuple = ([],[])

    # Start evaluation
    if mpi_pool is None:
        # Prepare arguments
        args = {}
        for key, val in zip(scatter_tuple[0], scatter_tuple[1]):
            if splitted:
                if len(val) != 1:
                    raise ValueError("Serial execution but splitted input is %d long" % len(val))
                args[key] = val[0]
            else:
                args[key] = val
        for key, val in zip(bcast_tuple[0], bcast_tuple[1]):
            args[key] = val
        for key, val in zip(dmem_arg_in_list, dmem_val_in_list):
            args[key] = val
        reduce_args = {}
        for key, val in zip(reduce_tuple[0], reduce_tuple[1]):
            if splitted:
                if len(val) != 1:
                    raise ValueError("Serial execution but splitted input is %d long" % len(val))
                reduce_args[key] = val[0]
            else:
                reduce_args[key] = val
        # Retrieve function
        if obj is not None:
            if isinstance(obj, str):
                f = getattr(obj_val, f)
            else:
                f = getattr(obj, f)
        # Evaluate
        fval = f(**args)
        # Reduce if necessary
        if reduce_obj is not None:
            fval = reduce_obj.outer_reduce(
                [ reduce_obj.inner_reduce(fval, **reduce_args) ], **reduce_args )
    else:
        # Prepare arguments
        obj_scatter = mpi_pool.split_data(scatter_tuple[1], scatter_tuple[0],
                                          splitted=splitted)
        obj_bcast = {}
        for key, val in zip(bcast_tuple[0], bcast_tuple[1]):
            obj_bcast[key] = val
        obj_args_reduce = mpi_pool.split_data(reduce_tuple[1], reduce_tuple[0],
                                              splitted=splitted)
        # Evaluate
        fval = mpi_pool.map(f,
                            obj_scatter=obj_scatter, obj_bcast=obj_bcast,
                            dmem_key_in_list=dmem_key_in_list,
                            dmem_arg_in_list=dmem_arg_in_list,
                            obj=obj,
                            reduce_obj=reduce_obj, reduce_args=obj_args_reduce)
        # Put pieces together and return
        if reduce_obj is None and concatenate:
            if isinstance(fval[0], tuple):
                out = []
                for i in range(len(fval[0])):
                    out.append( np.concatenate([fv[i] for fv in fval]) )
                fval = tuple( out )
            else:
                fval = np.concatenate(fval, axis=0)
    return fval
    
def mpi_map_alloc_dmem(f, scatter_tuple=None, bcast_tuple=None,
                       dmem_key_in_list=None, dmem_arg_in_list=None, dmem_val_in_list=None,
                       dmem_key_out_list=None,
                       obj=None, obj_val=None,
                       reduce_obj=None, reduce_tuple=None, 
                       mpi_pool=None, splitted=False, concatenate=True):
    r""" Interface for the parallel evaluation of a generic function on points ``x``

    Args:
      f (:class:`object` or :class:`str`): function or string identifying the
        function in object ``obj``
      scatter_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes.
      bcast_tuple (tuple): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be broadcasted to the processes.
      dmem_key_in_list (list): list of string containing the keys
        to be fetched (or created with default ``None`` if missing) from the
        distributed memory and provided as input to ``f``.
      dmem_val_in_list (list): list of objects corresponding to the keys defined
        in ``dmem_key_in_list``, used in case we are not executing in parallel
      dmem_key_out_list (list): list of keys to be assigned to the outputs
        beside the first one
      obj (object): object where the function ``f_name`` is defined
      obj_val (object): object to be used in case not executing in parallel and
        ``obj`` is a string
      reduce_obj (object): object :class:`ReduceObject` defining the reduce
        method to be applied (if any)   
      reduce_tuple (object): tuple containing 2 lists of ``[keys]`` and ``[arguments]``
        which will be scattered to the processes to be used by ``reduce_obj``
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processors
      splitted (bool): whether the scattering input is already splitted or not
      concatenate (bool): whether to concatenate the output (the output of ``f``
        must be a :class:`numpy.ndarray<numpy.ndarray>` object
    """
    # Init un-set arguments
    if scatter_tuple is None:
        scatter_tuple = ([],[])
    if bcast_tuple is None:
        bcast_tuple = ([],[])
    if dmem_key_in_list is None:
        dmem_key_in_list = []
    if dmem_arg_in_list is None:
        dmem_arg_in_list = []
    if dmem_val_in_list is None:
        dmem_val_in_list = []
    if dmem_key_out_list is None:
        dmem_key_out_list = []
    if reduce_tuple is None:
        reduce_tuple = ([],[])

    # Start evaluation
    if mpi_pool is None:
        # Prepare arguments
        args = {}
        for key, val in zip(scatter_tuple[0], scatter_tuple[1]):
            if splitted:
                if len(val) != 1:
                    raise ValueError("Serial execution but splitted input is %d long" % len(val))
                args[key] = val[0]
            else:
                args[key] = val
        for key, val in zip(bcast_tuple[0], bcast_tuple[1]):
            args[key] = val
        for key, val in zip(dmem_arg_in_list, dmem_val_in_list):
            args[key] = val
        reduce_args = {}
        for key, val in zip(reduce_tuple[0], reduce_tuple[1]):
            if splitted:
                if len(val) != 1:
                    raise ValueError("Serial execution but splitted input is %d long" % len(val))
                reduce_args[key] = val[0]
            else:
                reduce_args[key] = val
        # Retrieve function
        if obj is not None:
            if isinstance(obj, str):
                f = getattr(obj_val, f)
            else:
                f = getattr(obj, f)
        # Evaluate
        pars = f(**args)
        if not isinstance(pars, tuple):
            pars = (pars,)
    else:
        # Prepare arguments
        obj_scatter = mpi_pool.split_data(scatter_tuple[1], scatter_tuple[0],
                                          splitted=splitted)
        obj_bcast = {}
        for key, val in zip(bcast_tuple[0], bcast_tuple[1]):
            obj_bcast[key] = val
        obj_args_reduce = mpi_pool.split_data(reduce_tuple[1], reduce_tuple[0],
                                              splitted=splitted)
        # Evaluate
        pars = tuple([None] * len(dmem_key_out_list))
        mpi_pool.map_alloc_dmem(
            f, obj_scatter=obj_scatter, obj_bcast=obj_bcast,
            dmem_key_in_list=dmem_key_in_list,
            dmem_arg_in_list=dmem_arg_in_list,
            dmem_key_out_list=dmem_key_out_list,
            obj=obj,
            reduce_obj=reduce_obj, reduce_args=obj_args_reduce)
    return pars

def mpi_alloc_dmem(mpi_pool=None, **kwargs):
    r""" List of keyworded arguments to be allocated in the distributed memory.

    This executes only if an mpi_pool is provided.

    Args:
      mpi_pool (:class:`mpi_map.MPI_Pool<mpi_map.MPI_Pool>`): pool of processors
    """
    if mpi_pool is not None:
        mpi_pool.alloc_dmem(**kwargs)
    
#
# MPI REDUCE OPERATIONS
#
class SumChunkReduce(object):
    r""" Define the summation of the chunks operation.

    The chunks resulting from the output of the MPI evaluation are summed along
    their ``axis``.

    Args:
      axis (tuple [2]): tuple containing list of axes to be used in the
        :func:`sum<numpy.sum>` operation
    """
    def __init__(self, axis=None):
        self.axis = axis
    def inner_reduce(self, x, *args, **kwargs):
        return x
    def outer_reduce(self, x, *args, **kwargs):
        return np.sum(x, axis=self.axis)

class TupleSumChunkReduce(SumChunkReduce):
    r""" Define the summation of the chunks operation over list of tuples.

    The chunks resulting from the output of the MPI evaluation are summed along
    their ``axis``.

    Args:
      axis (tuple [2]): tuple containing list of axes to be used in the
        :func:`sum<numpy.sum>` operation
    """
    def outer_reduce(self, x, *args, **kwargs):
        out = []
        for i in range(len(x[0])):
            xin = [xx[i] for xx in x]
            out.append( super(TupleSumChunkReduce, self).outer_reduce(xin, *args, **kwargs) )
        return tuple(out)

class TensorDotReduce(object):
    r""" Define the reduce tensordot operation carried out through the mpi_map function

    Args:
      axis (tuple [2]): tuple containing list of axes to be used in the
        :func:`tensordot<numpy.tensordot>` operation
    """
    def __init__(self, axis):
        self.axis = axis
    def inner_reduce(self, x, w):
        if x.shape[self.axis[0]] > 0:
            return np.tensordot(x, w, self.axis)
        else:
            return 0.
    def outer_reduce(self, x, w):
        return sum( x )

class ExpectationReduce(TensorDotReduce):
    r""" Define the expectation operation carried out through the mpi_map function
    """
    def __init__(self):
        super(ExpectationReduce, self).__init__((0,0))

class AbsExpectationReduce(ExpectationReduce):
    r""" Define the expectation of the absolute value: :math:`\mathbb{E}[\vert {\bf X} \vert]`
    """
    def inner_reduce(self, x, w):
        return super(AbsExpectationReduce, self).inner_reduce(np.abs(x), w)

class TupleExpectationReduce(ExpectationReduce):
    r""" Define the expectation operation applied on a tuple

    If we are given a tuple :math:`(x_1,x_2)`, the inner reduce
    returns :math:`(\langle x_1,w\rangle , \langle x_2, w\rangle)`.

    Given a list of tuples :math:`\{(x_i,y_i\}_{i=0}^n`, the outer reduce
    gives :math:`(\sum x_i, \sum y_i)`.
    """
    def inner_reduce(self, x, w):
        out = []
        for xx in x:
            out.append( super(TupleExpectationReduce, self).inner_reduce(xx, w) )
        return tuple(out)
    def outer_reduce(self, x, w):
        out = []
        tdim = len(x[0])
        for i in range(tdim):
            xin = [xx[i] for xx in x]
            out.append( super(TupleExpectationReduce, self).outer_reduce(xin, w) )
        return tuple(out)

#
# Distributed operations
#
def distributed_sampling(
        d, qtype, qparams, mpi_pool=None):
    nprocs = mpi_pool.nprocs if mpi_pool is not None else 1
    qparams_split = qparams // nprocs
    qparams_reminder = qparams % nprocs
    qparams_list = [
        qparams_split if i >= qparams_reminder else qparams_split + 1
        for i in range(nprocs) ]
    mass_list = [ float(n)/float(qparams) for n in qparams_list ]
    scatter_tuple = (['qparams', 'mass'],
                     [qparams_list, mass_list])
    bcast_tuple = (['qtype'], [qtype])
    (x, w) = mpi_map_alloc_dmem(
        'quadrature',
        scatter_tuple=scatter_tuple, splitted=True,
        bcast_tuple=bcast_tuple,
        dmem_key_out_list=['x', 'w'],
        obj=d, mpi_pool=mpi_pool,
        concatenate=False)
    return (x, w)
        
#
# Total order multi index generation
#
def generate_total_order_midxs(max_order_list):
    r""" Generate a total order multi-index

    Given the list of maximums :math:`{\bf m}`, the returned set of
    multi-index :math:`I` is such that :math:`\sum_j^d {\bf_i}_j <= max {\bf m}`
    and :math:`{\bf i}_j <= {\bf m}_j`.
    """
    # Improve performances by writing it in cython.
    dim = len(max_order_list)
    max_order = max(max_order_list)
    # Zeros multi-index
    midxs_set = set()
    midx_new = tuple([0]*dim)
    if sum(midx_new) < max_order:
        midxs_old_set = set([ midx_new ]) # Containing increasable multi-indices
    else:
        midxs_old_set = set()
    midxs_set.add(midx_new)
    # Higher order multi-indices
    for i in range(1,max_order+1):
        midxs_new_set = set()
        for midx_old in midxs_old_set:
            for d in range(dim):
                if midx_old[d] < max_order_list[d]:
                    midx_new = list(midx_old)
                    midx_new[d] += 1
                    midxs_set.add( tuple(midx_new) )
                    if sum(midx_new) < max_order:
                        midxs_new_set.add( tuple(midx_new) )
        midxs_old_set = midxs_new_set
    # Transform to list of tuples
    midxs_list = list(midxs_set)
    return midxs_list

#
# Cost functions
#
def total_time_cost_function(
        ncalls, nevals, teval, ncalls_x_solve=None, new_nx=None):
    # Compute elapsed cost as total time
    t = teval.get('log_pdf',0)
    t += teval.get('grad_a_log_pdf',0)
    t += teval.get('tuple_grad_a_log_pdf',0)
    t += teval.get('hess_a_log_pdf',0)
    t += teval.get('action_hess_a_log_pdf',0)
    if new_nx is not None:
        # Compute forecasted time accordingly
        t += ncalls_x_solve.get('log_pdf',0) * new_nx * \
             teval.get('log_pdf',0) / nevals.get('log_pdf',1)
        t += ncalls_x_solve.get('grad_a_log_pdf',0) * new_nx * \
             teval.get('grad_a_log_pdf',0) / nevals.get('grad_a_log_pdf',1)
        t += ncalls_x_solve.get('tuple_grad_a_log_pdf',0) * new_nx * \
             teval.get('tuple_grad_a_log_pdf',0) / nevals.get('tuple_grad_a_log_pdf',1)
        t += ncalls_x_solve.get('hess_a_log_pdf',0) * new_nx * \
             teval.get('hess_a_log_pdf',0) / nevals.get('hess_a_log_pdf',1)
        t += ncalls_x_solve.get('action_hess_a_log_pdf',0) * new_nx * \
             teval.get('action_hess_a_log_pdf',0) / nevals.get('action_hess_a_log_pdf',1)
    return t
    
#
# Caching capabilities (decorator)
#
class cached(object):
    def __init__(self, sub_cache_list=[], caching=True):
        self.sub_cache_list = sub_cache_list
        self.caching = caching
    def __call__(self, f):
        @wraps(f)
        def wrapped(slf, *args, **kwargs):
            try:
                x = args[0]
            except IndexError:
                x = kwargs['x']
            idxs_slice = kwargs.get('idxs_slice', slice(None))
            cache = kwargs.get('cache', None)
            # Decide whether to cache output
            caching = (cache is not None) and self.caching
            # Retrieve from cache
            if caching:
                try:
                    (batch_set, vals) = cache[f.__name__]
                except KeyError as e:
                    new_cache = True
                else:
                    new_cache = False
                    if batch_set[idxs_slice][0]: # Checking only the first
                        return vals[idxs_slice]
            if cache is not None:
                # Init sub-cache if necessary
                for sub_name, sub_len in self.sub_cache_list:
                    try:
                        cache[sub_name + '_cache']
                    except KeyError:
                        if sub_len is None:
                            cache[sub_name + '_cache'] = {'tot_size': cache['tot_size']}
                        elif isinstance(sub_len, int):
                            cache[sub_name + '_cache'] = [
                                {'tot_size': cache['tot_size']}
                                for i in range(sub_len)]
                        elif isinstance(sub_len, str):
                            ll = getattr(slf, sub_len)
                            cache[sub_name + '_cache'] = [
                                {'tot_size': cache['tot_size']}
                                for i in range(ll)]
                        else:
                            raise TypeError("Type of sub_len not recognized")
            # Evaluate function
            out = f(slf, *args, **kwargs)
            # Store in cache
            if caching:
                if new_cache:
                    tot_size = cache['tot_size']
                    cache[f.__name__] = (
                        np.zeros(tot_size, dtype=bool),
                        np.empty((tot_size,)+out.shape[1:], dtype=np.float64))
                    (batch_set, vals) = cache[f.__name__]
                vals[idxs_slice] = out
                batch_set[idxs_slice] = True
            return out
        return wrapped

class cached_tuple(object):
    def __init__(self, commands=[], sub_cache_list=[], caching=True):
        if len(commands) == 0:
            raise AttributeError("You must provide at least one command, " + \
                                 "corresponding to the output on the tuple.")
        self.commands = commands
        self.sub_cache_list = sub_cache_list
        self.caching = caching
    def __call__(self, f):
        @wraps(f)
        def wrapped(slf, *args, **kwargs):
            try:
                x = args[0]
            except IndexError:
                x = kwargs['x']
            idxs_slice = kwargs.get('idxs_slice', slice(None))
            cache = kwargs.get('cache', None)
            # Decide whether to cache output
            caching = (cache is not None) and self.caching
            # Retrieve from cache
            if caching:
                out = [None for i in range(len(self.commands))]
                new_cache = [None for i in range(len(self.commands))]
                out_flag = True
                for i, cmd in enumerate(self.commands):
                    try:
                        (batch_set, vals) = cache[cmd]
                    except KeyError as e:
                        new_cache[i] = True
                        out_flag = False
                    else:
                        new_cache[i] = False
                        if batch_set[idxs_slice][0]: # Checking only the first
                            out[i] = vals[idxs_slice]
                        else:
                            out_flag = False
                if out_flag:
                    return tuple(out)
                else:
                    del out
            if cache is not None:
                # Init sub-cache if necessary
                for sub_name, sub_len in self.sub_cache_list:
                    try:
                        cache[sub_name + '_cache']
                    except KeyError:
                        if sub_len is None:
                            cache[sub_name + '_cache'] = {'tot_size': cache['tot_size']}
                        elif isinstance(sub_len, int):
                            cache[sub_name + '_cache'] = [
                                {'tot_size': cache['tot_size']}
                                for i in range(sub_len)]
                        elif isinstance(sub_len, str):
                            ll = getattr(slf, sub_len)
                            cache[sub_name + '_cache'] = [
                                {'tot_size': cache['tot_size']}
                                for i in range(ll)]
                        else:
                            raise TypeError("Type of sub_len not recognized")
            # Evaluate function
            feval_tuple = f(slf, *args, **kwargs)
            # Store in cache
            if caching:
                for i, (feval, cmd) in enumerate(zip(feval_tuple, self.commands)):
                    if new_cache[i]:
                        tot_size = cache['tot_size']
                        cache[cmd] = (
                            np.zeros(tot_size, dtype=bool),
                            np.empty((tot_size,)+feval.shape[1:], dtype=np.float64))
                    (batch_set, vals) = cache[cmd]
                    vals[idxs_slice] = feval
                    batch_set[idxs_slice] = True
            return feval_tuple
        return wrapped
        
def get_sub_cache(cache, *args):
    out = []
    for arg, dflt in args:
        try:
            out.append( cache[arg + "_cache"] )
        except TypeError:
            out.append( None if dflt is None else [None]*dflt )
    if len(out) > 1:
        return out
    else:
        return out[0]

#
# Taylor test for gradient and Hessian implementations
#
def taylor_test(x, dx, f, gf=None, hf=None, ahf=None, h=1e-4,
                fungrad=False, caching=False,
                args={}):
    r""" Test the gradient and Hessian of a function using the Taylor test.

    Using a Taylor expansion around :math:`{\bf x}`, we have

    .. math::

       f({\bf x}+h \delta{\bf x}) = f({\bf x})
           + h (\nabla f({\bf x}))^\top \delta{\bf x} 
           + \frac{h^2}{2} (\delta{\bf x})^\top \nabla^2 f({\bf x}) \delta{\bf x}
           + \mathcal{O}(h^3)

    Therefore
    
    .. math::

       \vert f({\bf x}+h \delta{\bf x}) - f({\bf x})
       - h (\nabla f({\bf x}))^\top \delta{\bf x} \vert = \mathcal{O}(h^2)

    and
    
    .. math::

       \vert f({\bf x}+h \delta{\bf x}) - f({\bf x})
       - h (\nabla f({\bf x}))^\top \delta{\bf x}
       - \frac{h^2}{2} (\delta{\bf x})^\top \nabla^2 f({\bf x}) \delta{\bf x} \vert
       = \mathcal{O}(h^3)

    Args:
      x (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): evaluation points :math:`{\bf x}`
      dx (:class:`ndarray<numpy.ndarray>` [:math:`m,d_x`]): perturbation direction
        :math:`\delta{\bf x}`
      f (function): function :math:`{\bf x} \mapsto f({\bf x})`. If ``fungrad==True``, then
        ``f`` is the mapping :math:`{\bf x} \mapsto (\nabla f({\bf x}), f({\bf x}))`.
      gf (function): gradient function :math:`{\bf x} \mapsto \nabla f({\bf x})`
      hf (function): Hessian function :math:`{\bf x} \mapsto \nabla^2 f({\bf x})`
      ahf (function): action of the Hessian function
        :math:`{\bf x},\delta{\bf x} \mapsto (\nabla f({\bf x}))^\top \delta{\bf x}`
      h (float): perturbation step
      fungrad (bool): whether ``f`` returns also the gradient or not.
      caching (bool): whether to pass a cache dictionary to the functions.
      args (dict): arguments to be passed to functions
    """
    if caching:
        args['cache'] = {'tot_size': x.shape[0]}
    # Compute at x
    if fungrad:
        fx, gfx = f(x, **args)
    else:
        fx = f(x, **args)
        gfx = gf(x, **args)
    if hf is not None:
        hfx = hf(x, **args)
        ahfx = np.einsum('...ij,...j->...i', hfx, dx)
    elif ahf is not None:
        ahfx = ahf(x, dx, **args)
    # Compute at x + h * dx
    if caching:
        args['cache'] = {'tot_size': x.shape[0]}
    if fungrad:
        fxhdx, _ = f(x + h * dx, **args)
    else:
        fxhdx = f(x + h * dx, **args)
    err_gx1 = np.abs( fxhdx - fx - h * np.einsum('...j,...j->...', gfx, dx) )
    if hf is not None or ahf is not None:
        err_hx1 = np.abs(
            fxhdx - fx - h * np.einsum('...j,...j->...', gfx, dx) - \
            h**2/2 * np.einsum('...i,...i->...', ahfx, dx) )
    # Halve the step
    h /= 2
    if caching:
        args['cache'] = {'tot_size': x.shape[0]}
    if fungrad:
        fxhdx, _ = f(x + h * dx, **args)
    else:
        fxhdx = f(x + h * dx, **args)
    err_gx2 = np.abs( fxhdx - fx - h * np.einsum('...j,...j->...', gfx, dx) )
    if hf is not None or ahf is not None:
        err_hx2 = np.abs(
            fxhdx - fx - h * np.einsum('...j,...j->...', gfx, dx) - \
            h**2/2 * np.einsum('...i,...i->...', ahfx, dx) )
    mrateg = np.min( np.log2(err_gx1/err_gx2) )
    print("Worst convergence rate gradient (should be 2): %.2f" % mrateg)
    if hf is not None or ahf is not None:
        mrateh = np.min( np.log2(err_hx1/err_hx2) )
        print("Worst convergence rate Hessian  (should be 3): %.2f" % mrateh)
