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
# Author: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import sys
import os
import os.path
import dill
import numpy as np

from . import AvailableOptions as AO
from .ScriptBase import Script

from TransportMaps.External import H5PY_SUPPORT, PLOT_SUPPORT
import TransportMaps.Distributions as DIST
import TransportMaps.Maps as MAPS
from TransportMaps.CLI.PostprocessBase import Postprocess

if PLOT_SUPPORT:
    import matplotlib.pyplot as plt
    
if H5PY_SUPPORT:
    import h5py

__all__ = ['AdaptivityPostprocess']

class AdaptivityPostprocess(Postprocess):

    cmd_usage_str = "Usage: tmap-adaptivity-postprocess "
    opts_usage_str = """  [--adapt-step=N --var-diag-conv]
"""
    usage_str = cmd_usage_str + Postprocess.opts_usage_str + opts_usage_str

    docs_descr_str = """DESCRIPTION
Given a file (--input) storing the transport maps pushing forward a base distribution
to a target distribution constructed through an adaptivity algorithm,
provides a number of diagnositic routines.
All files involved are stored and loaded using the python package dill and
an extra file OUTPUT.hdf5 is created to store big datasets in the hdf5 format.
In the following default values are shown in brackets."""
    docs_options_adapt_str = """OPTIONS - Adaptivity:
  --adapt-step=N          Run postprocessing analysis on the N-th map of the adaptivity
  --var-diag-conv         Plot the convergence in variance diagnostic vs. number
                            of coefficients
"""
    docs_options_str = Postprocess.docs_options_str + docs_options_adapt_str
    docs_str = docs_descr_str + docs_options_str

    def usage(self):
        print(AdaptivityPostprocess.usage_str)

    def description(self):
        print(AdaptivityPostprocess.docs_str)

    @property
    def long_options(self):
        return super(AdaptivityPostprocess, self).long_options + \
            [
                "adapt-step=", "var-diag-conv",
            ]

    def load_opts(self, opts):
        super(AdaptivityPostprocess, self).load_opts(opts)
        for opt, arg in opts:
            if opt == "--adapt-step":
                self.ADAPT_STEP = int(arg)
            elif opt == "--var-diag-conv":
                self.ADAPT_VAR_DIAG_CONV = True

    def __init__(self, argv):
        self.ADAPT_STEP = -1
        self.ADAPT_VAR_DIAG_CONV = False
        super(AdaptivityPostprocess, self).__init__(argv)

    def load(self):
        self.h5_file = None
        
        # Load data
        with open(self.INPUT, 'rb') as in_stream:
            self.stg = dill.load(in_stream)

        # Restore data
        self.base_distribution = self.stg.base_distribution
        self.target_distribution = self.stg.target_distribution
        try:
            self.builder = self.stg.builder
        except AttributeError:
            raise AttributeError(
                "The input file does not contain and adaptivity builder.")
        try:
            tm = self.builder.transport_map_list[self.ADAPT_STEP]
        except AttributeError:
            raise AttributeError(
                "The builder is not adaptive.")
        except IndexError:
            nmaps = len(self.builder.transport_map_list)
            raise IndexError(
                "Only %d maps are available. Required %d > %d." % (
                    nmaps, self.ADAPT_STEP, nmaps))
        self.tmap = MAPS.CompositeMap( self.stg.precond_map, tm )
        
        self.approx_base_distribution = DIST.PullBackTransportMapDistribution(
            self.tmap, self.target_distribution)
        self.approx_target_distribution = DIST.PushForwardTransportMapDistribution(
            self.tmap, self.base_distribution)
        self.dim = self.base_distribution.dim

        if self.ADAPT_STEP == -1:
            self.ADAPT_STEP = len(self.builder.transport_map_list)-1

        # Load output (dill file) if any
        if not os.path.exists(self.OUTPUT):
            self.postproc_data = {}
            with open(self.OUTPUT, 'wb') as out_stream:
                dill.dump(self.postproc_data, out_stream)
        with open(self.OUTPUT, 'rb') as in_stream:
            self.postproc_data = dill.load(in_stream)
        if not hasattr(self.postproc_data, 'adapt-steps'):
            self.postproc_data['adapt-steps'] = [{}] * len(self.builder.transport_map_list)
        self.postproc_data['adapt-steps'] += \
            [{}] * (len(self.builder.transport_map_list) - \
                    len(self.postproc_data['adapt-steps']))
        self.postproc_root = self.postproc_data['adapt-steps'][self.ADAPT_STEP]
        
        # Load output (hdf5 file) if any
        self.h5_file = h5py.File(self.OUTPUT + '.hdf5', 'a')
        ROOT_NAME = "adapt-step-%d" % self.ADAPT_STEP
        if ROOT_NAME not in self.h5_file:
            self.h5_file.create_group(ROOT_NAME)
        self.h5_root = self.h5_file[ROOT_NAME]

    def variance_diagnostic_convergence(self, mpi_pool):
        if self.ADAPT_VAR_DIAG_CONV:
            n_coeffs_list = [ self.builder.transport_map_list[i].n_coeffs
                              for i in range(len(self.builder.variance_diagnostic_list)) ]
            plt.figure()
            plt.semilogy(n_coeffs_list, self.builder.variance_diagnostic_list, '--o')
            plt.show(False)

    def run(self, mpi_pool):
        self.variance_diagnostic_convergence(mpi_pool)
        super(AdaptivityPostprocess, self).run(mpi_pool)