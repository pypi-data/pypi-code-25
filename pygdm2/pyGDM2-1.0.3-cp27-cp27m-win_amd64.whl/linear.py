# encoding: utf-8
#
#Copyright (C) 2017, P. R. Wiecha
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
linear optical effects

"""
import warnings

import numpy as np
import copy

from pyGDMfor import extinct as forExtinct
from pyGDMfor import nearfield as forNearfield
from pyGDMfor import multidipolefarfield as forFarfield



## (on linux) Set Stacksize for enabling passing large arrays to the fortran subroutines
import platform
if platform.system() == 'Linux':
    import resource
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))


#==============================================================================
# GLOBAL PARAMETERS
#==============================================================================




#==============================================================================
# EXCEPTIONS
#==============================================================================








#==============================================================================
# Linear Field processing functions
#==============================================================================
def extinct(sim, field_index):
    """Extinction, scattering and absorption corss-sections
    
    Calculates extinction, scattering and absorption crosssections
    for each wavelength of the GDM simulation
    
    
    Parameters
    ----------
    sim : :class:`.core.simulation`
        simulation description
    
    field_index : int
        index of evaluated self-consistent field to use for calculation. Can be
        obtained for specific parameter-set using :func:`.tools.get_closest_field_index`
        
    
    Returns
    -------
    extinct : float
        extinction cross-section
    
    scatter : float
        scattering cross-section
    
    absorpt : float
        apsorption cross-section
        
    
    Notes
    -----
    For the calculation of the cross-sections from the complex nearfield, 
    see e.g.: 
    Draine, B. T. & Flatau, P. J. **Discrete-dipole approximation for scattering 
    calculations.**
    Journal of the Optical Society of America, A 11, 1491 (1994).
    
    """
    if sim.E is None: 
        raise ValueError("Error: Scattering field inside the structure not yet evaluated. Run `core.scatter` simulation first.")
    
    ## --- incident field configuration
    field_params    = sim.E[field_index][0]
    wavelength      = field_params['wavelength']
    wavelengths     = np.asfortranarray([wavelength], dtype=sim.dtypef)
    
    ## -- get polarizability at wavelength
    alpha_spectral = np.transpose([sim.struct.getPolarizability(wavelength)])
    alpha_spectral = np.asfortranarray(alpha_spectral, dtype=sim.dtypec)
    
    ## --- fundamental and scattered field
    E0 = sim.efield.field_generator(sim.struct, **field_params)
    EX0, EY0, EZ0 = np.asfortranarray(E0, dtype=sim.dtypec).T
    E = sim.E[field_index][1]
    EX,  EY,  EZ  = np.asfortranarray(E, dtype=sim.dtypec).T
    
    ## --- use openmp-parallel fortran routine
    ext_sc, abs_sc = forExtinct(
                   elambda=wavelengths, 
                   cap=alpha_spectral, cn2=sim.struct.n2,
                   cex=EX, cey=EY, cez=EZ, cex0=EX0, cey0=EY0, cez0=EZ0)
    
    sca_sc = ext_sc - abs_sc
    
    return ext_sc, sca_sc, abs_sc



def nearfield(sim, field_index, r_probe):
    """Nearfield distribution in proximity of nanostructre
    
    For a given incident field, calculate the electro-magnetic field in the 
    proximity of the nanostructure (positions defined by `MAP`).
    
    Parameters
    ----------
    sim : :class:`.core.simulation`
        simulation description
    
    field_index : int
        index of evaluated self-consistent field to use for calculation. Can be
        obtained for specific parameter-set using :func:`.tools.get_closest_field_index`
    
    r_probe : tuple (x,y,z) or list of 3-lists/-tuples
        (list of) coordinate(s) to evaluate nearfield on. 
        Format: tuple (x,y,z) or list of 3 lists: [Xmap, Ymap, Zmap] 
        (the latter can be generated e.g. using :func:`.tools.generate_NF_map`)

    
    Returns
    -------
    4 lists of 6-tuples, complex : 
        - scattered Efield
        - total Efield (inlcuding fundamental field)
        - scattered Bfield
        - total Bfield (inlcuding fundamental field)
    
    the tuples are of shape (X,Y,Z, Ax,Ay,Az) with Ai the corresponding 
    complex field component
        
    
    Notes
    -----
    For details of the calculation of the scattered field outside the 
    nano-object using the self-consistent field inside the particle, see e.g.: 
    Girard, C. **Near fields in nanostructures.** 
    Reports on Progress in Physics 68, 1883–1933 (2005).

        
    """
    if sim.E is None: 
        raise ValueError("Error: Scattering field inside the structure not yet evaluated. Run `core.scatter` simulation first.")
    
    if len(np.shape(r_probe)) == 1:
        if len(r_probe) == 3:
            r_probe = [[r_probe[0]], [r_probe[1]], [r_probe[2]]]
        else: 
            raise ValueError("If 'r_probe' is tuple, must consist of *exactly* 3 elements!")
    elif len(np.shape(r_probe)) == 2:
        if np.shape(r_probe)[0] != 3 and np.shape(r_probe)[1] != 3:
            raise ValueError("'r_probe' must consist of *exactly* 3 elements!")
        if np.shape(r_probe)[0] != 3:
            r_probe = r_probe.T
    else:
        raise ValueError("wrong format for 'r_probe'. must consist of *exactly* 3 elements, either floats, or lists.")
    
    field_generator = sim.efield.field_generator
    xm, ym, zm      = sim.struct.geometry.T
    
    field_params    = sim.E[field_index][0]
    wavelength      = field_params['wavelength']
    
    cap = sim.struct.getPolarizability(wavelength)
    
    scattered_efield = sim.E[field_index][1]
    Ex = np.asfortranarray(scattered_efield.T[0], dtype=sim.dtypec)
    Ey = np.asfortranarray(scattered_efield.T[1], dtype=sim.dtypec)
    Ez = np.asfortranarray(scattered_efield.T[2], dtype=sim.dtypec)
    
    
    ## -- fundamental field - use dummy structure with map-definition as "geometry"
    dummy_struct = copy.deepcopy(sim.struct)
    dummy_struct.geometry = np.transpose(r_probe)
    E0 = field_generator(dummy_struct, returnField='E', **field_params)
    E0x = np.asfortranarray(E0.T[0], dtype=sim.dtypec)
    E0y = np.asfortranarray(E0.T[1], dtype=sim.dtypec)
    E0z = np.asfortranarray(E0.T[2], dtype=sim.dtypec)
    
    B0 = field_generator(dummy_struct, returnField='B', **field_params)
    B0x = np.asfortranarray(B0.T[0], dtype=sim.dtypec)
    B0y = np.asfortranarray(B0.T[1], dtype=sim.dtypec)
    B0z = np.asfortranarray(B0.T[2], dtype=sim.dtypec)
    
    
    ## -- coordinates to evaluate
    MAPx = np.asfortranarray(r_probe[0], dtype=sim.dtypef)
    MAPy = np.asfortranarray(r_probe[1], dtype=sim.dtypef)
    MAPz = np.asfortranarray(r_probe[2], dtype=sim.dtypef)
    
    cepx,cepy,cepz,cepx1,cepy1,cepz1, \
        cbpx,cbpy,cbpz,cbpx1,cbpy1,cbpz1 = forNearfield(
                 alambda=wavelength, space=sim.struct.spacing,
                 step=sim.struct.step, xm=xm, ym=ym, zm=zm,
                 cap=cap,
                 cn1=sim.struct.n1, cn2=sim.struct.n2, cn3=sim.struct.n3,
                 csolx=E0x, csoly=E0y, csolz=E0z, 
                 csolbx=B0x, csolby=B0y, csolbz=B0z,
                 cex=Ex, cey=Ey, cez=Ez, 
                 xmap=MAPx, ymap=MAPy, zmap=MAPz)
    
    
    return np.array([MAPx,MAPy,MAPz, cepx,cepy,cepz]).T, \
            np.array([MAPx,MAPy,MAPz, cepx1,cepy1,cepz1]).T, \
            np.array([MAPx,MAPy,MAPz, cbpx,cbpy,cbpz]).T, \
            np.array([MAPx,MAPy,MAPz, cbpx1,cbpy1,cbpz1]).T



def farfield(sim, field_index, 
             r=10000., tetamin=0, tetamax=np.pi/2., Nteta=10, Nphi=36, 
             polarizerangle='none', return_value='map'):
    """spatially resolved and polarization-filtered far-field scattering 
    
    For a given incident field, calculate the electro-magnetic field 
    (E-component) in the far-field around the nanostructure 
    (on a sphere of radius `r`).
    
    Parameters
    ----------
    sim : :class:`.core.simulation`
        simulation description
        
    field_index : int
        index of evaluated self-consistent field to use for calculation. Can be
        obtained for specific parameter-set using :func:`.tools.get_closest_field_index`
    
    r : float, default: 10000.
        radius of integration sphere (distance to coordinate origin in nm)
        
    tetamin, tetamax : float, float; defaults: 0, np.pi/2. (in [0, pi])
        minimum and maximum polar angle for semi-sphere in radians 
        (calculate from `tetamin` to `tetamax`)
        
    Nteta, Nphi : int, int; defaults: 10, 36
        number of polar and azimuthal angles on sphere to calculate,
        (angle ranges: polar = 0 - tetamax, azimuthal: 0 - 2*Pi)
        
    polarizerangle : float or 'none', default: 'none'
        optional polarization filter angle **in degrees**(!). If 'none' (default), 
        the total field-intensity is calculated (= no polarization filter)
    
    return_value : str, default: 'map'
        Values to be returned. Either 'map' (default) or 'integrated'.
          - "map" : (default) return spatially resolved farfield intensity at each spherical coordinate (5 lists)
          - "int_Es" : return the integrated scattered field (as float)
          - "int_E0" : return the integrated fundamental field (as float)
          - "int_Etot" : return the integrated total field (as float)
    
    
    Returns
    -------
    return_value == "map" : 5 arrays of shape (Nteta, Nphi) : 
        - tetalist : teta angles
        - philist : phi angles
        - I_sc : intensity of scattered field, 
        - I_tot : intensity of total field (I_tot=|E_sc+E_0|^2), 
        - I0 : intensity of incident field
    
    return_typ == "int_XX" : float
        integrated total intensity over specified solid angle
        
    
    Notes
    -----
    For details of the asymptotic (non-retarded) far-field propagators for a 
    dipole above a substrate, see e.g.:
    Colas des Francs, G. & Girard, C. & Dereux, A. **Theory of near-field 
    optical imaging with a single molecule as light source.** 
    The Journal of Chemical Physics 117, 4659–4666 (2002)
        
    """
    if sim.E is None: 
        raise ValueError("Error: Scattering field inside the structure not yet evaluated. Run `core.scatter` simulation first.")
    
    if str(polarizerangle).lower() == 'none':
        polarizer = 0
    else:
        polarizer = polarizerangle * np.pi/180.
    
    if np.pi < tetamax < 0:
        raise ValueError("`tetamax` out of range, must be in [0, pi]")
    
    
    field_params    = sim.E[field_index][0]
    wavelength      = field_params['wavelength']
    
    dteta = (tetamax-tetamin)/float(Nteta-1)
    dphi = 2.*np.pi/float(Nphi)
    
#==============================================================================
#     Scattered field
#==============================================================================
    ## --- environment
    eps0, eps1 = sim.struct.n1**2, sim.struct.n2**2
    
    ## --- dipoles: Positions and their electric polarization
    xm, ym, zm = sim.struct.geometry.T    
    alpha = sim.struct.getPolarizability(wavelength)
    scattered_efield = sim.E[field_index][1]
    cpx = np.asfortranarray(scattered_efield.T[0] * alpha, dtype=sim.dtypec)
    cpy = np.asfortranarray(scattered_efield.T[1] * alpha, dtype=sim.dtypec)
    cpz = np.asfortranarray(scattered_efield.T[2] * alpha, dtype=sim.dtypec)
    
    ## --- calculate scattered field
    tetalist, philist, IntensInt, IntensIntPol, IntensPol, Intens, \
                cex_sc, cey_sc, cez_sc, ce_sc_pol = \
                              forFarfield(wavelength, Nteta, Nphi, 
                                          tetamin, tetamax,
                                          r, eps0, eps1, polarizer,
                                          xm, ym, zm,
                                          cpx, cpy, cpz)

#==============================================================================
#     Fundamental field
#==============================================================================
    ## --- fundamental field - use dummy structure with 
    ## --- spherical map-definition as "geometry"
    xff = (r * np.sin(tetalist) * np.cos(philist)).flatten()
    yff = (r * np.sin(tetalist) * np.sin(philist)).flatten()
    zff = (r * np.cos(tetalist)).flatten()
    MAP = [xff, yff, zff]
    
    field_generator = sim.efield.field_generator
    dummy_struct = copy.deepcopy(sim.struct)
    dummy_struct.geometry = np.transpose(MAP)
    E0 = field_generator(dummy_struct, returnField='E', **field_params)
    ce0x = np.asfortranarray(E0.T[0], dtype=sim.dtypec).reshape((Nteta, Nphi))
    ce0y = np.asfortranarray(E0.T[1], dtype=sim.dtypec).reshape((Nteta, Nphi))
    ce0z = np.asfortranarray(E0.T[2], dtype=sim.dtypec).reshape((Nteta, Nphi))
    
    if str(polarizerangle).lower() != 'none':
        ## --- fundamental E-field parallel and perpendicular to scattering plane
        ce0_par  = ( ce0x * np.cos(tetalist) * np.cos(philist) + 
                     ce0y * np.sin(philist) * np.cos(tetalist) - 
                     ce0z * np.sin(tetalist) )
        ce0_perp = ( ce0x * np.sin(philist) - ce0y * np.cos(philist) )
        ## --- fundamental E-field parallel to polarizer
        ce0_pol  = ( ce0_par * np.cos(polarizer - philist) - 
                     ce0_perp * np.sin(polarizer - philist) )

#==============================================================================
#     Intensities with and without fundamental field / polarizer
#==============================================================================
    ## --- total field (no polarizer)
    I_sc  = Intens
    I0    = ( np.abs(ce0x)**2 + np.abs(ce0y)**2 + np.abs(ce0z)**2 )
    I_tot = ( np.abs(cex_sc + ce0x)**2 + 
              np.abs(cey_sc + ce0y)**2 + 
              np.abs(cez_sc + ce0z)**2 )
    
    ## --- optionally: with polarizer
    if str(polarizerangle).lower() != 'none':
        I_sc  = IntensPol
        I0    = ( np.abs(ce0_pol)**2 )
        I_tot = ( np.abs(ce_sc_pol + ce0_pol)**2 )
        
    if return_value.lower() == 'map':
        return tetalist, philist, I_sc, I_tot, I0
    else:
        d_solid_surf = r**2 * np.sin(tetalist) * dteta*dphi
        if return_value.lower() == 'int_es':
            return np.sum(I_sc*d_solid_surf)
        elif return_value.lower() == 'int_e0':
            return np.sum(I0*d_solid_surf)
        elif return_value.lower() == 'int_etot':
            return np.sum(I_tot*d_solid_surf)
        else:
            raise ValueError("Parameter 'return_value' must be one of ['map', 'int_es', 'int_e0', 'int_etot'].")


    
def heat(sim, field_index, power_scaling_e0=1.0, return_value='total', return_units='nw'):
    """calculate the total induced heat in the nanostructure
    
    Parameters
    ----------
    sim : :class:`.core.simulation`
        simulation description
    
    field_index : int
        index of evaluated self-consistent field to use for calculation. Can be
        obtained for specific parameter-set using :func:`.tools.get_closest_field_index`
    
    power_scaling_e0 : float, default: 1
        incident laser power scaling. power_scaling_e0 = 1 corresponds 
        to 1 mW per micron^2. See [1].
    
    return_value : str, default: 'total'
        Values to be returned. Either 'total' (default) or 'structure'.
        
        - "total" : return the total deposited heat in nW (float)
        
        - "structure" : return spatially resolved deposited heat at each 
          meshpoint in nW (list of tuples [x,y,z,q])
    
    return_units : str, default: "nw"
        units of returned heat values, either "nw" or "uw" (nano or micro Watts)
    
    
    Returns
    -------
    Q : float *or* list of tuples [x,y,z,q]
    
        - `return_value`="structure" : (return float)
          total deposited heat in nanowatt (optionally in microwatt). 

        - `return_value`="structure" : (return list of tuples [x,y,z,q])
          The returned quantity *q* is the total deposited heat 
          at mesh-cell position [x,y,z] in nanowatt. To get the heating 
          power-density, please divide by the mesh-cell volume.
    
    
    Notes
    -----
    For details on heat/temperature calculations and raster-scan simulations, see:
    
    [1] Baffou, G., Quidant, R. & Girard, C.: **Heat generation in plasmonic 
    nanostructures: Influence of morphology**
    Applied Physics Letters 94, 153109 (2009)
    
    [2] Teulle, A. et al.: **Scanning optical microscopy modeling in nanoplasmonics** 
    Journal of the Optical Society of America B 29, 2431 (2012).


    """
    if sim.E is None: 
        raise ValueError("Error: Scattering field inside the structure not yet evaluated. Run `core.scatter` simulation first.")
    
    power_scaling_e0 *= 0.01    # for mW/cm^2
    
    field_params    = sim.E[field_index][0]
    wavelength      = field_params['wavelength']
    k0 = 2*np.pi / wavelength
    
    ## --- Factor allowing to have the released power in nanowatt 
    released_power_scaling = 100.
    
    ## --- polarizabilities and electric fields
    alpha = sim.struct.getPolarizability(wavelength)
    E = sim.E[field_index][1]
    ex, ey, ez = E.T
    
    ## --- total deposited heat
#    I_e = np.abs(ex**2 + ey**2 + ez**2)
    I_e = (np.abs(ex)**2 + np.abs(ey)**2 + np.abs(ez)**2)
    
    ## heat at each meshpoint in nW/nm^3
    q = 4.*np.pi *np.imag(alpha) * I_e * k0 * power_scaling_e0 * released_power_scaling
    
    ## --- optional conversion to micro watts
    if return_units.lower() == 'uw':
        q /= 1.0E3
    
    if return_value == 'total':
        return np.sum(q)
    elif return_value in ['structure', 'struct']:
        x,y,z = sim.struct.geometry.T
        return np.concatenate([[x],[y],[z],[q]]).T
    else:
        raise ValueError("`return_value` must be one of ['total', 'structure', 'struct'].")



def temperature(sim, field_index, r_probe, 
                kappa_env=0.6, kappa_subst=None, incident_power=1.0):
    """calculate the temperature rise at locations outside the nano-particle
    
    Calculate the temperature increase close to a optically excited 
    nanostructure using the approach described in [2] and [3] (Ref. [3] 
    introduces a further correction term for particles lying on a substrate)
    
    Parameters
    ----------
    sim : :class:`.core.simulation`
        simulation description
    
    field_index : int
        index of evaluated self-consistent field to use for calculation. Can be
        obtained for specific parameter-set using :func:`.tools.get_closest_field_index`
    
    r_probe : tuple (x,y,z) or list of 3-lists/-tuples
        (list of) coordinate(s) to evaluate nearfield on. 
        Format: tuple (x,y,z) or list of 3 lists: [Xmap, Ymap, Zmap] 
        (the latter can be generated e.g. using :func:`.tools.generate_NF_map`)
    
    kappa_env : float, default: 0.6
        heat conductivity of environment. default: kappa_env = 0.6 (water). 
        (air: kappa=0.024, for more material values see e.g. [4]). In W/mK.
    
    kappa_subst : float, default: None
        heat conductivity of substrate. default: None --> same as substrate. 
        Using the mirror-image technique described in [3]. (glass: kappa=0.8)
    
    incident_power : float, default: 1.0
        incident laser power density in mW per micron^2. See also [1].
    
    
    Returns
    -------
    if evaluating at a single position, D_T : float
        temperature increase in Kelvin at r_probe
    
    if evaluating at a list of positions, list of tuples [x, y, z, D_T] 
        where D_T is the temperature increase in Kelvin at (x,y,z), which
        are the positions defined by `r_probe`
    
    Notes
    -----
    For details on heat/temperature calculations and raster-scan simulations, see:
    
    [1] Baffou, G., Quidant, R. & Girard, C.: **Heat generation in plasmonic 
    nanostructures: Influence of morphology**
    Applied Physics Letters 94, 153109 (2009)
    
    [2] Baffou, G., Quidant, R. & Girard, C.: **Thermoplasmonics modeling: 
    A Green’s function approach** 
    Phys. Rev. B 82, 165424 (2010)

    [3] Teulle, A. et al.: **Scanning optical microscopy modeling in nanoplasmonics**
    Journal of the Optical Society of America B 29, 2431 (2012).
    
    
    For the thermal conductivity of common materials, see:
    
    [4] Hugh D Young, Francis Weston Sears: **University Physics**, *chapter 15*,
    8th. edition: Addison-Wesley, 1992
    (see also e.g.: http://hyperphysics.phy-astr.gsu.edu/hbase/Tables/thrcn.html)

    """
    kappa_subst = kappa_subst or kappa_env
    
    if sim.E is None: 
        raise ValueError("Error: Scattering field inside the structure not yet evaluated. Run `core.scatter` simulation first.")
    
    if kappa_subst == kappa_env and sim.struct.n1 != sim.struct.n2:
        warnings.warn("Substrate and environment have different indices but same heat conductivity.")
    if kappa_subst != kappa_env and sim.struct.n1 == sim.struct.n2:
        warnings.warn("Substrate and environment have same ref.index but different heat conductivity.")
    
    incident_power *= 0.01          # for mW/cm^2
    released_power_scaling = 100.   # output in nW
    
    field_params    = sim.E[field_index][0]
    wavelength      = field_params['wavelength']
    
    n2 = sim.struct.n2
    k_env = 2*np.pi* np.real(n2) / wavelength
    
    
    
    ## --- main heat generation function
    def calc_heat_single_position(sim, r_probe):
        ## --- polarizability and field in structure
        alpha = sim.struct.getPolarizability(wavelength)
        E = sim.E[field_index][1]
        ex, ey, ez = E.T
        
        ## --- meshpoint distance to probe, polarizabilities and electric fields
        r_mesh = sim.struct.geometry
        dist_probe = np.sqrt( np.sum( np.power((np.array(r_probe) - r_mesh), 2), axis=1) )
        
        ## --- mirror structure below substrate for heat reflection at substrate
        if kappa_subst != kappa_env:
            r_mesh_mirror = copy.deepcopy(sim.struct.geometry)
            r_mesh_mirror.T[2] *= -1
            dist_probe_mirror = np.sqrt( np.sum( np.power((np.array(r_probe) - r_mesh_mirror), 2), axis=1) ) 
        
        ## --- temperature rise at r_probe
#        I_e = np.abs(ex**2 + ey**2 + ez**2)
        I_e = np.abs(ex)**2 + np.abs(ey)**2 + np.abs(ez)**2
#        I_e = ex.real**2 + ex.imag**2 + ey.real**2 + ey.imag**2 + ez.real**2 + ez.imag**2
        q = np.imag(alpha) * I_e * k_env * incident_power * released_power_scaling
        D_T = np.sum( q / dist_probe )
        if kappa_subst != kappa_env:
            D_T += np.sum( q / dist_probe_mirror ) * (kappa_subst - kappa_env)/(kappa_subst + kappa_env)
        D_T /= kappa_env
        
        if np.isnan(D_T):
            print D_T, np.sum(I_e), np.imag(alpha[0])
        
        return D_T
    
    
    ## --- SINGLE POSITION:
    if len(np.shape(r_probe)) == 1 or len(r_probe) == 1:
        D_T = calc_heat_single_position(sim, r_probe)
    ## --- MULTIPLE POSITIONS:
    else:
        D_T = []
        if np.shape(r_probe)[1] != 3:
            r_probe = np.transpose(r_probe)
        for i in r_probe:
            D_T.append([i[0], i[1], i[2], 
                        calc_heat_single_position(sim, i)])
        D_T = np.array(D_T)
    
    return D_T





def decay_eval(sim, SBB, mx,my,mz, verbose=False):
    """evaluate decay rate of electric or magnetic dipole transition
    
    Evaluate the decay rate modification of a dipole with complex amplitude
    (mx,my,mz) using pre-calculated tensors (:func:`.core.decay_rate`).
    
    Parameters
    ----------
      sim : :class:`.core.simulation`
        simulation description
      
      SBB : int or list of lists
          index of wavelength in `sim` or tensor-list as returned by 
          :func:`.core.decay_rate`
      
      mx,my,mz : float 
          x/y/z amplitude of dipole transition vector
      
      verbose : bool default=False
          print some runtime info
    
    Returns
    -------
      gamma_map: list of lists [x,y,z, gamma]
          Each element consists of:
           - x,y,z: coordinates of evaluation position
           - gamma: normalized decay-rate (real) gamma / gamma_0 at each map-position
      
    Notes
    -----
    For detailed information about the underlying formalism, see:
    Wiecha, P. R., Girard, C., Cuche, A., Paillard, V. & Arbouet, A. 
    **Decay Rate of Magnetic Dipoles near Non-magnetic Nanostructures.** 
    arXiv:1707.07006 (2017)
      
    """
    import fields
    if sim.efield.field_generator == fields.dipole_electric:
        dp_type = 'electric'
    elif sim.efield.field_generator == fields.dipole_magnetic:
        dp_type = 'magnetic'
    else:
        raise ValueError("Wrong incident field: `decay_rate` requires the " + 
                         "incident field to be " + 
                         "either an electric or a magnetic dipole emitter. " +
                         "Please use `fields.dipole_electric` or " +
                         "`fields.dipole_magnetic`.")
    
    ## --- evaluation coordinates of dipole
    xyz = [[pos['x0'], pos['y0'], pos['z0']] for pos in sim.efield.kwargs_permutations]
    MAP = np.array(xyz)
    
    if type(SBB) == int:
        if sim.S_P is None: 
            raise ValueError("Error: Decay tensors not yet evaluated. Run `core.decay_rate` first.")
        SBB = sim.S_P[SBB]
        
    wavelength = SBB[0]
    SBB = SBB[1]
        
    ak0 = 2.*np.pi / (wavelength)
    
    if verbose:
        print "decay-rate evaluated using:"
        print "  - wavelength: {}nm".format(wavelength)
        print "  - dipole type: {}".format(dp_type)
        print "  - dipole vector: ({}, {}, {})".format(mx,my,mz)
    
    
    ## --- normalization
    ## normalize by chi/step^3 (divide by step**3 because cell-volume is already 
    ##                          taken into account in GDM polarizabilities)
    sim.struct.getNormalization(wavelength)
    Chi = sim.struct.getPolarizability(wavelength)
    if len(np.unique(Chi)) != 1:
        raise ValueError("Anisotropic structures not supported by the decay " +
                         "rate calculation at the moment! Please use a " +
                         "constant material dispersion for the whole structure.")
    Chi = Chi[0]
    normSBB = Chi / sim.struct.step**3  
    
    
    ## calc. unitary dipole orientation: divide by dipole length
    meg = np.sqrt(mx**2 + my**2 + mz**2)
    mu = np.array([mx, my, mz]) / meg
    
    ## vacuum value for decay
    gamma_0 = 1
    
    ## vacuum speed of light in cm/s
    c = 2.99792E11
    
    ## get propagator SBB
    from scipy.linalg import norm
    gamma_map = np.zeros( (len(MAP),4) )
    for i,R in enumerate(MAP):
        gamma_map[i][0] = R[0]
        gamma_map[i][1] = R[1]
        gamma_map[i][2] = R[2]
        gamma_map[i][3] = (gamma_0 + (3./2.) * (1./ak0**3) * gamma_0 * 
                           np.dot(np.dot(mu, (normSBB * SBB[i]).imag), mu))
        
        ## --- outside structure
        if abs(sorted(norm(sim.struct.geometry - R, axis=1))[0]) >= sim.struct.step:
            gamma_map[i][3] = (gamma_0 + (3./2.) * (1./ak0**3) * gamma_0 * 
                               np.dot(np.dot(mu, (normSBB * SBB[i]).imag), mu))
        ## --- inside structure
        else:
            if dp_type == 'magnetic':
                raise Exception("Magnetic LDOS cannot be calculated `inside` the particle.")
            gamma_map[i][3] = (gamma_0 + (3./2.) * (1./ak0**3) * gamma_0 * 
                               np.dot(np.dot(mu, (1./sim.struct.step**3   * SBB[i]).imag), mu))
#            gamma_map[i][3] = (gamma_0 + (3./2.) * (1./ak0**3) * gamma_0 * 
#                               np.dot(np.dot(mu, (SBB[i]).imag), mu))
    
    return gamma_map

