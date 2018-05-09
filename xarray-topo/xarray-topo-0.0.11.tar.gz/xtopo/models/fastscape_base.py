"""Implementation of FastScape's base model using the xarray-simlab
framework.

This base model allows to simulate the evolution of topography as a
result of block uplift vs. channel erosion by stream power law.

"""
import numpy as np
import xsimlab as xs

from ..algos import flow_routing
from ..algos import bedrock_channel
from ..algos import hillslope_erosion


@xs.process
class Grid2D(object):
    """A 2-dimensional regular grid."""

    x_size = xs.variable(description='nb. of nodes in x')
    y_size = xs.variable(description='nb. of nodes in y')
    x_length = xs.variable(description='total grid length in x')
    y_length = xs.variable(description='total grid length in y')

    x_spacing = xs.variable(intent='out')
    y_spacing = xs.variable(intent='out')

    x = xs.variable(dims='x', intent='out')
    y = xs.variable(dims='y', intent='out')

    def initialize(self):
        self.x = np.linspace(0, self.x_length, self.x_size)
        self.y = np.linspace(0, self.y_length, self.y_size)

        self.x_spacing = self.x_length / (self.x_size - 1)
        self.y_spacing = self.y_length / (self.y_size - 1)


@xs.process
class ClosedBoundaryFaces(object):
    """Boundary conditions where each face of the grid in
    both x and y is considered as a boundary.

    """
    x_size = xs.foreign(Grid2D, 'x_size')
    y_size = xs.foreign(Grid2D, 'y_size')

    active_nodes = xs.variable(dims=('y', 'x'), intent='out')

    def initialize(self):
        mask = np.ones((self.y_size, self.x_size), dtype=bool)
        bound_indexers = [0, -1, (slice(None), 0), (slice(None), -1)]

        for idx in bound_indexers:
            mask[idx] = False

        self.active_nodes = mask


@xs.process
class TotalErosion(object):
    """Sum of all (vertical) erosion processes."""

    erosion_vars = xs.group('erosion')
    erosion = xs.variable(dims=('y', 'x'), intent='out')

    def run_step(self, *args):
        self.erosion = sum((v for v in self.erosion_vars))


@xs.process
class TotalRockUplift(object):
    """Sum of all (vertical) rock uplift processes."""

    uplift_vars = xs.group('uplift')
    uplift = xs.variable(dims=('y', 'x'), intent='out')

    def run_step(self, *args):
        self.uplift = sum((v for v in self.uplift_vars))


@xs.process
class Topography(object):
    """Topography evolution resulting from the balance between
    total rock uplift and total erosion.

    This process has also two diagnostics available:
    topographic slope and curvature.

    """
    elevation = xs.variable(dims=('y', 'x'), intent='inout',
                            description='topographic elevation')
    total_erosion = xs.foreign(TotalErosion, 'erosion')
    total_uplift = xs.foreign(TotalRockUplift, 'uplift')

    slope = xs.on_demand(dims=('y', 'x'),
                         description='topographic local slope')
    curvature = xs.on_demand(dims=('y', 'x'),
                             description='topographic local curvature',
                             attrs={'units': '1/m'})

    def initialize(self):
        self.elevation_change = np.zeros_like(self.elevation)

    def run_step(self, *args):
        self.elevation_change = self.total_uplift - self.total_erosion

    def finalize_step(self):
        self.elevation += self.elevation_change

    @slope.compute
    def _compute_slope(self):
        raise NotImplementedError()

    @curvature.compute
    def _compute_curvature(self):
        raise NotImplementedError()


@xs.process
class FlowRouterD8(object):
    """Compute flow receivers using D8 and also compute the node
    ordering stack following Braun and Willet method.

    """
    pit_method = xs.variable()

    x_size = xs.foreign(Grid2D, 'x_size')
    y_size = xs.foreign(Grid2D, 'y_size')
    x_spacing = xs.foreign(Grid2D, 'x_spacing')
    y_spacing = xs.foreign(Grid2D, 'y_spacing')
    active_nodes = xs.foreign(ClosedBoundaryFaces, 'active_nodes')
    elevation = xs.foreign(Topography, 'elevation')

    receivers = xs.variable(dims=('y', 'x'), intent='out')
    dist2receivers = xs.variable(dims=('y', 'x'), intent='out')
    ndonors = xs.variable(dims=('y', 'x'), intent='out')
    donors = xs.variable(dims=('y', 'x', 'd8'), intent='out')
    stack = xs.variable(dims=('y', 'x'), intent='out')
    basins = xs.variable(dims=('y', 'x'), intent='out')
    outlets = xs.variable(dims=('y', 'x'), intent='out')
    pits = xs.variable(dims=('y', 'x'), intent='out')

    def initialize(self):
        nx = self.x_size
        ny = self.y_size
        nnodes = ny * nx
        self.nnodes = nnodes

        self._receivers = np.arange(nnodes, dtype=np.intp)
        self._dist2receivers = np.zeros(nnodes)

        self._ndonors = np.zeros(nnodes, dtype=np.uint8)
        self._donors = np.empty((nnodes, 8), dtype=np.intp)
        self._stack = np.empty(nnodes, dtype=np.intp)
        self._basins = np.empty(nnodes, dtype=np.intp)
        self._outlets = np.empty(nnodes, dtype=np.intp)
        self._pits = np.empty(nnodes, dtype=np.intp)

        self._elevation = self.elevation.ravel()
        self._active_nodes = self.active_nodes.ravel()

        self.receivers = self._receivers.reshape((ny, nx))
        self.dist2receivers = self._dist2receivers.reshape((ny, nx))

        self.ndonors = self._ndonors.reshape((ny, nx))
        self.donors = self._donors.reshape((ny, nx, 8))
        self.stack = self._stack.reshape((ny, nx))
        self.basins = self._basins.reshape((ny, nx))
        self.outlets = self._outlets.reshape((ny, nx))
        self.pits = self._pits.reshape((ny, nx))

        if self.pit_method == 'no_resolve':
            self.correct_receivers = False
        else:
            self.correct_receivers = True

        self._nbasins = 0
        self._npits = 0

    def run_step(self, *args):
        flow_routing.reset_receivers(self._receivers, self.nnodes)
        flow_routing.compute_receivers_d8(
            self._receivers, self._dist2receivers,
            self._elevation,
            self.x_size, self.y_size,
            self.x_spacing, self.y_spacing)
        flow_routing.compute_donors(self._ndonors, self._donors,
                                    self._receivers, self.nnodes)
        flow_routing.compute_stack(self._stack,
                                   self._ndonors, self._donors,
                                   self._receivers,
                                   self.nnodes)

        self._nbasins = flow_routing.compute_basins(
            self._basins, self._outlets,
            self._stack, self._receivers, self.nnodes)
        self._npits = flow_routing.compute_pits(
            self._pits, self._outlets, self._active_nodes, self._nbasins)

        if self.correct_receivers and self._npits:
            flow_routing.correct_flowrouting(
                self._receivers, self._dist2receivers,
                self._ndonors, self._donors,
                self._stack, self._nbasins, self._basins,
                self._outlets,
                self._active_nodes, self._elevation,
                self.x_size, self.y_size,
                self.x_spacing, self.y_spacing,
                method=self.pit_method)
            self._nbasins = flow_routing.compute_basins(
                self._basins, self._outlets,
                self._stack, self._receivers, self.nnodes)


@xs.process
class PropagateArea(object):
    """Compute drainage area."""

    dx = xs.foreign(Grid2D, 'x_spacing')
    dy = xs.foreign(Grid2D, 'y_spacing')
    receivers = xs.foreign(FlowRouterD8, 'receivers')
    stack = xs.foreign(FlowRouterD8, 'stack')

    area = xs.variable(dims=('y', 'x'), intent='out',
                       description='drainage area')

    def initialize(self):
        self.grid_cell_area = self.dx * self.dy
        self.area = np.empty(self.receivers.shape)

        self._area = self.area.ravel()
        self._receivers = self.receivers.ravel()
        self._stack = self.stack.ravel()

    def run_step(self, *args):
        self._area[:] = self.grid_cell_area
        flow_routing.propagate_area(self._area, self._stack, self._receivers)


@xs.process
class StreamPower(object):
    """Compute channel erosion using the stream power law."""

    k_coef = xs.variable(description='stream-power constant')
    m_exp = xs.variable(description='stream-power drainage area exponent')
    n_exp = xs.variable(description='stream-power slope exponent')

    erosion = xs.variable(dims=('y', 'x'), intent='out', group='erosion')

    receivers = xs.foreign(FlowRouterD8, 'receivers')
    dist2receivers = xs.foreign(FlowRouterD8, 'dist2receivers')
    stack = xs.foreign(FlowRouterD8, 'stack')
    area = xs.foreign(PropagateArea, 'area')
    elevation = xs.foreign(Topography, 'elevation')

    def initialize(self):
        self.tolerance = 1e-3
        self.nnodes = self.elevation.size
        self.erosion = np.zeros_like(self.elevation)

        self._erosion = self.erosion.ravel()
        self._receivers = self.receivers.ravel()
        self._dist2receivers = self.dist2receivers.ravel()
        self._stack = self.stack.ravel()
        self._area = self.area.ravel()
        self._elevation = self.elevation.ravel()

    def run_step(self, dt):
        bedrock_channel.erode_spower(
            self._erosion, self._elevation,
            self._stack, self._receivers,
            self._dist2receivers, self._area,
            self.k_coef,
            self.m_exp,
            self.n_exp,
            dt, self.tolerance, self.nnodes)


@xs.process
class LinearDiffusion(object):
    """Compute hillslope erosion as linear diffusion process."""

    k_coef = xs.variable(description='diffusivity')

    erosion = xs.variable(dims=('y', 'x'), intent='out', group='erosion')

    elevation = xs.foreign(Topography, 'elevation')
    dx = xs.foreign(Grid2D, 'x_spacing')
    dy = xs.foreign(Grid2D, 'y_spacing')
    nx = xs.foreign(Grid2D, 'x_size')
    ny = xs.foreign(Grid2D, 'y_size')

    def initialize(self):
        self.erosion = np.zeros_like(self.elevation)

    def run_step(self, dt):
        hillslope_erosion.erode_linear_diffusion(
            self.erosion, self.elevation,
            self.k_coef, dt,
            self.dx, self.dy,
            self.nx, self.ny)


@xs.process
class BlockUplift(object):
    """Compute block uplift."""

    u_coef = xs.variable(dims=[(), ('y', 'x')], description='uplift rate')

    uplift = xs.variable((), intent='out', group='uplift')
    active_nodes = xs.foreign(ClosedBoundaryFaces, 'active_nodes')

    def initialize(self):
        self.mask = self.active_nodes
        self.uplift = np.zeros_like(self.mask, dtype='f')

    def run_step(self, dt):
        u_rate = self.u_coef

        if not np.isscalar(u_rate):
            u_rate = u_rate[self.mask]

        self.uplift[self.mask] = u_rate * dt


fastscape_base_model = xs.Model(
    {'grid': Grid2D,
     'boundaries': ClosedBoundaryFaces,
     'block_uplift': BlockUplift,
     'flow_routing': FlowRouterD8,
     'area': PropagateArea,
     'spower': StreamPower,
     'diffusion': LinearDiffusion,
     'erosion': TotalErosion,
     'uplift': TotalRockUplift,
     'topography': Topography}
)
