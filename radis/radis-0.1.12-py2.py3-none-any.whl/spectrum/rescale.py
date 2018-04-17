# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 13:30:16 2017

@author: erwan

Functions to update Spectrum with new spectral quantities that can be derived
from existing ones, or rescale path_length or mole_fraction, or add overpopulations

Most of these are binded as methods to the Spectrum class, but stored here to
unload the spectrum.py file 

"""

from __future__ import print_function, absolute_import, division, unicode_literals
import numpy as np
from numpy import log as ln
from numpy import inf, exp
from radis.misc.debug import printdbg
from radis.spectrum.utils import CONVOLUTED_QUANTITIES, NON_CONVOLUTED_QUANTITIES
from radis.lbl.equations import calc_radiance
from radis.misc.basics import all_in, any_in
from radis.misc.basics import compare_lists
from warnings import warn
from six import string_types

# List of all spectral variables sorted by priority during recomputation 
# (ex: first get abscoeff, then try to calculate emisscoeff, etc.)
ordered_keys = [ 
         'abscoeff',
         'emisscoeff',
         'absorbance',
         'radiance_noslit',
         'transmittance_noslit',
         'emissivity',
         'emissivity_noslit',
         'radiance',
         'transmittance',
         ]
# ... variables that cannot be rescaled (or not implemented):
non_rescalable_keys = ['abscoeff_continuum']
# ... Check we have everyone (safety check!):
# ... if it fails here, then we may have added a new key without adding a scaling 
# ... method. Explicitely add it in non_rescalableçkeys so an error is raised 
# ... if trying to rescale a Spectrum that has such a quantity
assert compare_lists(ordered_keys+non_rescalable_keys, CONVOLUTED_QUANTITIES+NON_CONVOLUTED_QUANTITIES,
                     verbose=False)
    
def _build_update_graph(spec, optically_thin=None, equilibrium=None, path_length=None,
                        no_change=False):
    ''' Find inheritances properties (dependencies and equivalences) between all spectral 
    variables based on the spectrum conditions (equilibrium, optically thin, 
    known path length?)
    
    Parameters
    ----------
    
    spec: Spectrum
        a :class:`~radis.spectrum.spectrum.Spectrum` object
        
    Other Parameters
    ----------------
    
    optically_thin: boolean
        know whether the Spectrum should be considered optically thin to build
        the equivalence graph tree. If None, the value stored in the Spectrum is used. 
        Default None
        
    equilibrium: boolean
        know whether the Spectrum should be considered at equilibrium to build
        the equivalence graph tree. If None, the value stored in the Spectrum is used. 
        Default None
        
    path_length: boolean
        know whether the path length is given to build the equivalence graph tree. 
        If None, ``path_length`` is looked up in the Spectrum condition. Default None
        
    no_change: boolean
        if True, signals that we are somehow rescaling without changing path length
        nor mole fractions, i.e, all quantities can be recomputed from themselves...
    
    Returns
    -------
    
    derivation: dict
        {spectral_quantity: [list of combinations of spectral quantities needed to calculate it]}
    
    Examples
    --------
    
    to recompute a Spectrum under nonequilibrium, non optically thin case
    (note that all paths are not there yet)::
        
        {'abscoeff': [['absorbance']],
         'absorbance': [['transmittance_noslit'], ['abscoeff']],
         'emisscoeff': [['radiance_noslit', 'abscoeff']],
         'radiance_noslit': [['emisscoeff', 'abscoeff']],
         'transmittance_noslit': [['absorbance']]}
    
    a Spectrum under nonequilibrium, with optically thin case::
        
        {'abscoeff': [['absorbance']],
         'absorbance': [['transmittance_noslit'], ['abscoeff']],
         'emisscoeff': [['radiance_noslit']],
         'radiance_noslit': [['emisscoeff']],
         'transmittance_noslit': [['absorbance']]}
        
    a Spectrum under equilibrium (everything leads to everything)::
        
        {'abscoeff': [['absorbance'],
                      ['absorbance'],
                      ['emisscoeff'],
                      ['emissivity_noslit'],
                      ['transmittance'],
                      ['radiance'],
                      ['radiance_noslit'],
                      ['transmittance_noslit']],
         'absorbance': [['transmittance_noslit'],
                      ['abscoeff'],
                      ['abscoeff'],
                      ['emisscoeff'],
                      ['emissivity_noslit'],
                      ['transmittance'],
                      ['radiance'],
                      ['radiance_noslit'],
                      ['transmittance_noslit']],
         etc. }
        
    
    '''
    
    # Get defaults 
    if path_length is None: path_length = 'path_length' in spec.conditions
    if optically_thin is None: optically_thin = spec.is_optically_thin()
    if equilibrium is None: equilibrium = spec.is_at_equilibrium()
    slit = ('slit_function' in spec.conditions and 'slit_unit' in spec.conditions
            and 'norm_by' in spec.conditions)
    
    all_keys = [
             'abscoeff',
             'absorbance',
             'emisscoeff',
             'emissivity_noslit',
             'transmittance',
             'radiance',
             'radiance_noslit',
             'transmittance_noslit',
             ]
    assert all_in(all_keys, CONVOLUTED_QUANTITIES+NON_CONVOLUTED_QUANTITIES)
    
    # Build edges of relationships
    derivation = {             # {keys, [list of keys]}
        'transmittance_noslit':[['absorbance']],
        'absorbance':[['transmittance_noslit']],
        }
    
    def derives_from(what, *from_keys):
        ''' Writes that quantity ``what`` can be infered by having all quantities
        ``from_keys`` 
        
        Examples
        --------
        
        Radiance can be infered from emisscoeff if optically thin::
        
            derives_from('radiance_noslit', 'emisscoeff')
            
        Else abscoeff would also be needed::
            
            derives_from('emisscoeff', ['radiance_noslit', 'abscoeff'])
        
        '''
        for k in from_keys:
            if isinstance(k, string_types):
                k = [k]
            try:
                derivation[what].append(k)
            except KeyError:
                derivation[what] = [k]
    
    # Build more equivalence relationships if path_length is given
    # ------------------------------------------------------------
    # TODO: complete that, list is not exhaustive yet. 
    # Duplicates are removed afterwards anyway
    # 
    # Note for Developers: all derives_from relationship should correspond to a  
    # rescale method that was implemented. Only the developer can know that!
    # If a rescaled relationship is implemetend but not added here it wont be 
    # used by the code when trying to add all quantities. If a relationship is 
    # added here but not implemented it will crash during rescale (and explain why)
    
    # no change: case where we are rescaling without changing path length nor 
    # mole fractions, i.e, all initial quantities can be recomputed from themselves...
    if no_change:
        for k in all_keys:
            derives_from(k, [k])
    
    # Deal with case where we know path_length:
    if path_length:
        derives_from('abscoeff', ['absorbance'])
        derives_from('absorbance', ['abscoeff'])
        if optically_thin:
            derives_from('radiance_noslit', ['emisscoeff'])
            derives_from('emisscoeff', ['radiance_noslit'])
        else:
            derives_from('radiance_noslit', ['emisscoeff', 'abscoeff'])
            derives_from('emisscoeff', ['radiance_noslit', 'abscoeff'])

    if slit:
        if __debug__: printdbg('... build_graph: slit given > convoluted keys can be recomputed')
        derives_from('radiance', ['radiance_noslit'])
        derives_from('transmittance', ['transmittance_noslit'])
        derives_from('emissivity', ['emissivity_noslit'])

    if equilibrium:
        if __debug__: printdbg('... build_graph: equilibrium > all keys derive from one')
        # Anything can be recomputed from anything
        for key in all_keys:
            if key in NON_CONVOLUTED_QUANTITIES:
                all_but_k = [[k] for k in all_keys if k != key]
                derives_from(key, *all_but_k)
    
    # ------------------------------------------------------------
    
    if __debug__: 
        printdbg('_build_update_graph: dependence/equivalence tree:')
        printdbg(derivation)
    
    return derivation

def get_redundant(spec):
    ''' Returns a dictionary of all spectral quantities in spectrum and whether
    they are redundant
    
    Use
    -------
    
    redundant = get_redundant(spec)
    
    '''
    
    derivation_graph = _build_update_graph(spec)
    
    activated = dict().fromkeys(ordered_keys, False)
    for k in spec.get_vars():
        activated[k] = True
    redundant = dict().fromkeys(ordered_keys, False)
    
    # Parse graph
    for key in ordered_keys[::-1]:    # roots
        if key in derivation_graph:
            for from_keys in derivation_graph[key]:
#                if [key] == from_keys:
#                    # that you can be recomputed from yourself doesnt make you redundant
#                    continue
                if all([activated[k] and not redundant[k] for k in from_keys]):
                    redundant[key] = True
                    continue
        else:
            del redundant[key]
            # Should look at dependencies again ??
            
    return redundant

def _path_is_complete(list_of_keys, computed_keys):
    return all([computed_keys[k] for k in list_of_keys])
    
def get_reachable(spec): #, derivation_graph):
    ''' Get the list of all quantities that can be derived from current available
    quantities, based on given spec conditions 
    
    Parameters
    ----------
    
    spec: Spectrum
        a :class:`~radis.spectrum.spectrum.Spectrum` object
        
    Returns
    -------
    
    reachable: list
        list of quantities that can be calculated from available information
        
    Notes
    -----
    
    Algorithm::
        
        for all quantities, starting from the last:
            for all possible ways to compute them
                if valid, add quantity to reachable list, and restart
                else, continue
            
    '''
    
    # Get inheritance links based on Spectrum conditions (equilibrium, optically thin, etc.)
    derivation_graph = _build_update_graph(spec)
    
#    activated = dict().fromkeys(ordered_keys, False)
    reachable = dict().fromkeys(ordered_keys, False)
    for k in spec.get_vars():
        reachable[k] = True
    
    # Parse graph
    restart = True
    while restart:
        restart = False
        for key in ordered_keys[::-1]:    # roots
            if key in derivation_graph:
                for from_keys in derivation_graph[key]:  # all different ways to compute this value
                    if _path_is_complete(from_keys, reachable):  # if all are reachable then we can reach this new value
                        if not reachable[key]:
                            reachable[key] = True
                            restart = True   # status changed -> restart?                            
        
    return reachable

def get_recompute(spec, wanted, no_change=False, true_path_length=None): #, derivation_graph):
    ''' Get the list of all quantities that need to be recomputed to get the 
    ``wanted`` quantities based on given spec conditions 
    (does not recompute yet!)
    
    Parameters
    ----------
    
    spec: Spectrum
        a :class:`~radis.spectrum.spectrum.Spectrum` object
        
    wanted: list
        list of quantities to recompute

        
    Other Parameters
    ----------------
    
    no_change: boolean
        if True, signals that we are somehow rescaling without changing path length
        nor mole fractions, i.e, all quantities can be recomputed from themselves...
    
    true_path_length: boolean
        know whether the path length is given to build the equivalence graph tree. 
        If None, ``path_length`` is looked up in the Spectrum condition. Default None
        
    Returns
    -------
    
    recompute: list
        list of quantities needed
        
    Notes
    -----
    
    Algorithm::
        
        for all quantities:
            for all possible ways to compute them
                if valid, add quantity to reachable list, and restart
                else, continue
            
    '''
    
    # Get inheritance links based on Spectrum conditions (equilibrium, optically thin, etc.)
    derivation_graph = _build_update_graph(spec, path_length=true_path_length,
                                           no_change=no_change)
    
#    activated = dict().fromkeys(ordered_keys, False)
    # Store two dictionaries, that characterize, at a given instant, all quantities
    # that we had to recompute, and all quantities that can be recomputed from these 
    recompute = dict().fromkeys(ordered_keys, False)
    for k in spec.get_vars():     # start from all quantities we have
        recompute[k] = True
    for k in wanted:              # add all quantities we want
        recompute[k] = True
#    reachable = dict().fromkeys(ordered_keys, False)
#    for k in spec.get_vars():   # start from all quantities we have
#        reachable[k] = True
        
    def parse_tree(recompute):
        for key in ordered_keys:
            if key in wanted:       # find a way to recompute it:
                can_recompute_key = False
                for from_keys in derivation_graph[key]:   # all different ways to compute this value
                    if _path_is_complete(from_keys, recompute):  # if all are recomputed already they we can recompute this new value
                        # we can reach this quantity
                        recompute[key] = True
                        can_recompute_key = True
                        break
                if not can_recompute_key:
                    if __debug__:
                        printdbg("... get_recompute: Can't recompute {0} with current keys: {1}. Finding something else".format
                          (key, [k for k in from_keys if recompute[k]]))
#                    # cant recompute this quantity. Let's force recomputation 
#                    def get_best_path():
#                        new_recompute_set = recompute.copy()
#                        for k in ordered_keys:
#                            # let's add a new quantity to recompute
#                            if new_recompute_set[k]:
#                                # we already have this quantity
#                                continue
#                            elif not any([k in from_keys for from_keys in derivation_graph[key]]):
#                                # this quantity (k) doesnt participate in calculating from_keys
#                                continue
#                            else:
#                                # let's calculate it
#                                
                    # cant recompute this quantity. Let's force recomputation 
                    # of a given path. We'll arbitrary use the one will the fewer
                    # amount of not already recomputed quantities
                    score_non_recomputed_per_path = {}
                    for from_keys in derivation_graph[key]:
                        score = sum([not recompute[k] for k in from_keys])
                        # if several paths have same score the last will be chosen:
                        score_non_recomputed_per_path[score] = from_keys   
                    # get the path with the minimum of values to recompute:
                    min_path = score_non_recomputed_per_path[min(score_non_recomputed_per_path)]
                    # Add all these variables to the recompute list, and restart
                    for k in min_path:
                        recompute[k] = True
                        if __debug__: 
                            printdbg('... get_recompute: Added new quantity to recompute list:', k)
                    return recompute, True
         # reached the end with no change, no need to restart
        return recompute, False
                    
    # Parse graph
    restart = True
    while restart:
        recompute, restart = parse_tree(recompute)
        
    recompute = [k for k in recompute if recompute[k]]
        
    if __debug__:
        printdbg('... get_recompute: List of quantities to recompute: ', recompute)
        
    return recompute



def update(spec, quantity='all', optically_thin='default', verbose=True):
    ''' Calculate missing quantities that can be derived from the current quantities
    and conditions
    
    e.g: if path_length and emisscoeff are given, radiance_noslit can be recalculated
    if in an optically thin configuration, else if abscoeff is also given 
    
    
    Parameters    
    ----------
    
    spec: Spectrum
    
    quantity: str
        name of the spectral quantity to recompute. If 'same', only the quantities
        in the Spectrum are recomputed. If 'all', then all quantities that can
        be derived are recomputed. Default 'all'. 

    optically_thin: True, False, or 'default'
        determines whether to calculate radiance with or without self absorption.
        If 'default', the value is determined from the self_absorption key
        in Spectrum.conditions. If not given, False is taken. Default 'default'
        Also updates the self_absorption value in conditions (creates it if 
        doesnt exist)
        
    '''

    # Check inputs
    # ------------

    # Get path length
    if 'path_length' in list(spec.conditions.keys()):
        path_length = spec.conditions['path_length']
        true_path_length = True
    else:
        path_length = 1        # some stuff can still be updated.
        true_path_length = False
        
    # Update optically thin
    if optically_thin not in [True, False, 'default']:
        raise ValueError("optically_thin must be one of True, False, 'default'")
    if optically_thin == 'default':
        if 'self_absorption' in list(spec.conditions.keys()):
            optically_thin = not spec.conditions['self_absorption']
        else:
            optically_thin = False
    old_self_absorption = spec.conditions.get('self_absorption')
    if old_self_absorption != (not optically_thin):
        spec.conditions['self_absorption'] = not optically_thin
        if verbose:
            print(('self absorption set to:', spec.conditions['self_absorption']))

    initial = spec.get_vars()

    # This is where everything happens:
    # ---------------------------------
    _recalculate(spec, quantity, 
                 path_length, path_length,   # same path length (absolute value can matter)
                 1, 1,                       # same mole fractions (only the ratio matters)
                 true_path_length=true_path_length,
                 verbose=verbose)
    
    # Output
    # ------
    
    # Get list of new quantities 
    new_q = [k for k in spec.get_vars() if k not in initial]
    if verbose:
        print(('New quantities added: {0}'.format(new_q)))
        
    # Final checks
    for k in new_q:
        # make sure units exist
        if not k in spec.units:
            raise ValueError('{0} added but unit is unknown'.format(k))
        
# Rescale functions

# ... absorption coefficient
def rescale_abscoeff(spec, rescaled, initial, old_mole_fraction, new_mole_fraction,
                      old_path_length, waveunit, units, extra, true_path_length):
    '''
    
    Parameters    
    ----------
    
    spec: Spectrum
    
    old_path_length: float
        path length in cm
        
    '''
    
    unit = None
    
    # case where we recomputed it already (somehow... ex: no_change signaled)
    if 'abscoeff' in rescaled:
        if __debug__: printdbg('... rescale: abscoeff was scaled already')
        assert 'abscoeff' in units
        return rescaled, units

    # First get initial abscoeff
    # ---------------------
    if 'abscoeff' in initial:
        _, abscoeff = spec.get('abscoeff', wunit=waveunit)
    elif 'absorbance' in initial and true_path_length: # aka: true path_lengths given
        if __debug__: printdbg('... rescale: abscoeff k1 = A/L1')
        _, A = spec.get('absorbance', wunit=waveunit)
        abscoeff = A/old_path_length                      # recalculate
        unit = 'cm-1'
    elif 'transmittance_noslit' in initial and true_path_length:
        if __debug__: printdbg('... rescale: abscoeff k1 = -ln(T1)/L1')
        # Get abscoeff from transmittance
        _, T1 = spec.get('transmittance_noslit', wunit=waveunit)
        
        # We'll have a problem if the spectrum is optically thick
        b = (T1== 0)  # no transmittance: optically thick mask
        if b.sum()>0:
            msg = "Transmittance is satured. Can't infer abscoeff. Please give absorbance"
            if 'abscoeff' in extra: # cant calculate this one but let it go
                abscoeff = None
                if __debug__: printdbg(msg)
            else:
                raise ValueError(msg)
            
        # Else, let's calculate it
        abscoeff = -ln(T1)/old_path_length         # recalculate
        unit = 'cm-1'
    elif 'abscoeff' in extra: # cant calculate this one but let it go
        abscoeff = None
    else:
        raise ValueError("Can't rescale abscoeff if transmittance_noslit ({0}) ".format(
                            'transmittance_noslit' in initial)+\
                         'or absorbance ({0}), '.format('absorbance' in initial)+\
                         'and true_path_length ({0}) '.format(true_path_length)+\
                         'are not given. Use optically_thin?')
        
    # Then export rescaled value
    # --------------------
    if abscoeff is not None:
        if __debug__: printdbg('... rescale: abscoeff k2 = k1 * N2/N1')
        abscoeff *= new_mole_fraction / old_mole_fraction     # rescale
        rescaled['abscoeff'] = abscoeff
    if unit is not None:
        units['abscoeff'] = unit

    return rescaled, units

# ... all, if equilibrium and abscoeff was rescaled
def _recompute_all_at_equilibrium(spec, rescaled, wavenumber, Tgas, 
                                  new_path_length, true_path_length,
                                  units):
    ''' 
    
    Parameters    
    ----------
    
    rescaled: dict
        abscoeff must be rescaled already 
    '''
    
    def get_unit_radiance():
        return spec.units.get('radiance_noslit', 'mW/cm2/sr/nm')
    
    def get_unit_emisscoeff(unit_radiance):
        if '/cm2' in unit_radiance:
            return unit_radiance.replace('/cm2', '/cm3')
        else:
            return unit_radiance + '/cm'  # will be simplified by Pint afterwards

    assert true_path_length
    
    abscoeff = rescaled['abscoeff']
    path_length = new_path_length
    
    absorbance = abscoeff*path_length

    # Generate output quantities
    transmittance_noslit = exp(-absorbance)
    emissivity_noslit = 1 - transmittance_noslit
    radiance_noslit = calc_radiance(wavenumber, emissivity_noslit, Tgas, 
                                    unit=get_unit_radiance())
    b = (abscoeff==0)  # optically thin mask
    emisscoeff = np.empty_like(abscoeff)
    emisscoeff[b] = radiance_noslit[b]/path_length              # recalculate (opt thin)
    emisscoeff[~b] = radiance_noslit[~b]/(1-transmittance_noslit[~b])*abscoeff[~b]    # recalculate (non opt thin)
    
    # ----------------------------------------------------------------------

    rescaled['absorbance'] = absorbance
    rescaled['transmittance_noslit'] = transmittance_noslit
    rescaled['emissivity_noslit'] = emissivity_noslit
    rescaled['radiance_noslit'] = radiance_noslit
    rescaled['emisscoeff'] = emisscoeff
    
    
    units['abscoeff'] = 'cm_1'
    units['absorbance'] = '-ln(I/I0)'
    units['transmittance_noslit'] = 'I/I0'
    units['emissivity_noslit'] = 'eps'
    units['radiance_noslit'] = get_unit_radiance()
    units['emisscoeff'] = get_unit_emisscoeff(units['radiance_noslit'])
    
    return rescaled, units

# ... emission coefficient
def rescale_emisscoeff(spec, rescaled, initial, old_mole_fraction, new_mole_fraction,
                        old_path_length, optically_thin, waveunit, units, 
                        extra, true_path_length):
    '''
    
    Parameters    
    ----------
    
    spec: Spectrum
    '''
    
    unit = None
    def get_unit(unit_radiance):
        if '/cm2' in unit_radiance:
            return unit_radiance.replace('/cm2', '/cm3')
        else:
            return unit_radiance + '/cm'  # will be simplified by Pint afterwards

    # case where we recomputed it already (somehow... ex: no_change signaled)
    if 'emisscoeff' in rescaled:
        if __debug__: printdbg('... rescale: emisscoeff was scaled already')
        assert 'emisscoeff' in units
        return rescaled, units

    # Firt get initial emisscoeff j1
    # -------------------

    if 'emisscoeff' in initial:
        if __debug__: printdbg('... rescale: emisscoeff j1 = j1')
        _, emisscoeff = spec.get('emisscoeff', wunit=waveunit, Iunit=units['emisscoeff'])
        
    elif 'radiance_noslit' in initial and true_path_length and optically_thin:
        if __debug__: printdbg('... rescale: emisscoeff j1 = I1/L1')
        _, I = spec.get('radiance_noslit', wunit=waveunit, Iunit=units['radiance_noslit'])
        emisscoeff = I/old_path_length   # recalculate
        unit = get_unit(units['radiance_noslit'])
        
    elif ('radiance_noslit' in initial and true_path_length and
          'abscoeff' in initial):
        if __debug__: printdbg('... rescale: emisscoeff j1 = k1*I1/(1-exp(-k1*L1))')
        # get emisscoeff from (initial) abscoeff and (initial) radiance
        _, I = spec.get('radiance_noslit', wunit=waveunit, Iunit=units['radiance_noslit'])
        _, k = spec.get('abscoeff', wunit=waveunit, Iunit=units['abscoeff'])
        
        # Recalculate in the optically thin range (T=1) and elsewhere
        b = (k==0)  # optically thin mask
        emisscoeff = np.empty_like(k)
        # ... optically thin case
        emisscoeff[b] = I[b]/old_path_length              # recalculate (opt thin)
        
        # ... non optically thin case:
        # ... recalculate transmittance from abscoeff
        T_b = exp(-k[~b]*old_path_length) 
        # ... and solve the RTE on an homogeneous slab
        emisscoeff[~b] = k[~b]*I[~b]/(1-T_b)              # recalculate (non opt thin)
        unit = get_unit(units['radiance_noslit'])
        
    elif ('radiance_noslit' in initial and true_path_length and
          'transmittance_noslit' in initial):
        if __debug__: printdbg('... rescale: emisscoeff j1 = k1*I1/(1-T1)')
        # get emisscoeff from (initial) transmittance and (initial) radiance
        _, I = spec.get('radiance_noslit', wunit=waveunit, Iunit=units['radiance_noslit'])
        _, T = spec.get('transmittance_noslit', wunit=waveunit, Iunit=units['transmittance_noslit'])
        
        # Recalculate in the optically thin range (T=1) and elsewhere
        b = (T==1)  # optically thin mask
        emisscoeff = np.empty_like(T)
        # ... optically thin case
        emisscoeff[b] = I[b]/old_path_length              # recalculate (opt thin)
        
        # ... non optically thin case:
        # ... recalculate abscoeff from transmittance
        T_b = T[~b]
        k_b = -ln(T_b)/old_path_length       
        # ... and solve the RTE on an homogeneous slab
        emisscoeff[~b] = k_b*I[~b]/(1-T_b)              # recalculate (non opt thin)
        unit = get_unit(units['radiance_noslit'])
        
    else:
        if optically_thin:
            msg = "Can't calculate emisscoeff if true path_length ({0})".format(true_path_length)+\
                  "and initial radiance_noslit ({0}) are not all given".format(
                          'radiance_noslit' in initial)
            if 'emisscoeff' in extra: # cant calculate this one but let it go
                emisscoeff = None
                if __debug__: printdbg(msg)
            else:
                raise ValueError(msg)
        else:
            msg = "Trying to get the emission coefficient (emisscoeff) in non optically "+\
                  "thin case. True path_length ({0}), radiance_noslit ({1}) ".format(
                          true_path_length, 'radiance_noslit' in initial)+\
                  "and abscoeff ({0}) are needed but not all given. ".format(
                          'abscoeff' in initial)+\
                  "Try optically_thin? See known Spectrum conditions with "+\
                  "print(Spectrum)"
            if 'emisscoeff' in extra: # cant calculate this one but let it go
                emisscoeff = None
                if __debug__: printdbg(msg)
            else:
                raise ValueError(msg)
            
    # Then rescale and export
    # -----------
    if emisscoeff is not None:
        if __debug__: printdbg('... rescale: emisscoeff j2 = j1 * N2/N1')
        # Now rescale for mole fractions
        emisscoeff *= new_mole_fraction / old_mole_fraction   # rescale
        rescaled['emisscoeff'] = emisscoeff
    if unit is not None:
        units['emisscoeff'] = unit

    return rescaled, units

# ... absorbance
def rescale_absorbance(spec, rescaled, initial, old_mole_fraction, new_mole_fraction,
                        old_path_length, new_path_length, waveunit, units, 
                        extra, true_path_length):
    '''
    
    Parameters    
    ----------
    
    spec: Spectrum
    '''
    
    unit = None

    # case where we recomputed it already (somehow... ex: no_change signaled)
    if 'absorbance' in rescaled:
        if __debug__: printdbg('... rescale: absorbance was scaled already')
        assert 'absorbance' in units
        return rescaled, units

    # Rescale!
    if 'absorbance' in initial:
        if __debug__: printdbg('... rescale: absorbance A2 = A1*N2/N1*L2/L1')
        _, absorbance = spec.get('absorbance', wunit=waveunit, Iunit=units['absorbance'])
        absorbance *= new_mole_fraction / old_mole_fraction   # rescale
        absorbance *= new_path_length / old_path_length       # rescale
    elif 'abscoeff' in rescaled and true_path_length:
        if __debug__: printdbg('... rescale: absorbance A2 = j2*L2')
        abscoeff = rescaled['abscoeff']        # mole_fraction already scaled
        absorbance = abscoeff*new_path_length               # calculate
        unit = '-ln(I/I0)'
    else:
        msg = 'Cant recalculate absorbance if scaled absoeff '+\
              '({0}) and true path_length ({1}) are not given'.format(
                    'abscoeff' in rescaled, true_path_length)
        if 'absorbance' in extra:  # cant calculate this one but let it go
            absorbance = None
            if __debug__: printdbg(msg)
        else:
            raise ValueError(msg)
            
    # Export rescaled value
    if absorbance is not None:
        rescaled['absorbance'] = absorbance
    if unit is not None:
        units['absorbance'] = unit

    return rescaled, units

# ... transmittance
def rescale_transmittance_noslit(spec, rescaled, initial, old_mole_fraction, new_mole_fraction,
                                  old_path_length, new_path_length, waveunit, units, extra):
    '''
    
    Parameters    
    ----------
    
    spec: Spectrum
    '''
    
    unit = None    
    def get_unit():
        return 'I/I0'

    # case where we recomputed it already (somehow... ex: no_change signaled)
    if 'transmittance_noslit' in rescaled:
        if __debug__: printdbg('... rescale: transmittance_noslit was scaled already')
        assert 'transmittance_noslit' in units
        return rescaled, units

    # Rescale
    if 'absorbance' in rescaled:
        if __debug__: printdbg('... rescale: transmittance_noslit T2 = exp(-A2)')
        absorbance = rescaled['absorbance'] # N and L already scaled
        transmittance_noslit = exp(-absorbance)           # recalculate
        unit = get_unit()
    elif 'transmittance_noslit' in initial:
        if __debug__: printdbg('... rescale: transmittance_noslit T2 = '+\
                        'exp( ln(T1) * N2/N1 * L2/L1)')
        # get transmittance from initial transmittance
        _, T1 = spec.get('transmittance_noslit', wunit=waveunit, Iunit=units['transmittance_noslit'])
        
        
        # We'll have a problem if the spectrum is optically thick
        b = (T1 == 0)  # optically thick mask
        if b.sum()>0 and (new_mole_fraction < old_mole_fraction or 
                new_path_length < old_path_length):
            # decreasing mole fractions/ path length could increase the transmittance
            # but this information was lost in the saturation
            msg = 'Transmittance is satured. Cant rescale. Please give absorbance'
            if 'transmittance_noslit' in extra: # cant calculate this one but let it go
                transmittance_noslit = None
                if __debug__: printdbg(msg)
            else:
                raise ValueError(msg)
        # Else, just get absorbance
        absorbance = -ln(T1)
        absorbance *= new_mole_fraction / old_mole_fraction     # rescale
        absorbance *= new_path_length / old_path_length         # rescale
        transmittance_noslit = exp(-absorbance)
    else:
        msg = 'Missing data to rescale transmittance. Expected scaled absorbance ({0})'.format(
                'absorbance' in rescaled)
#        +' or scaled abscoeff ({0}) and true_path_length ({1})'.format(
#                'abscoeff' in rescaled, true_path_length)
        if 'transmittance_noslit' in extra: # cant calculate this one but let it go
            transmittance_noslit = None
            if __debug__: printdbg(msg)
        else:
            raise ValueError(msg)
            
    # Export rescaled value
    if transmittance_noslit is not None:
        rescaled['transmittance_noslit'] = transmittance_noslit
    if unit is not None:
        units['transmittance_noslit'] = unit

    return rescaled, units

def rescale_transmittance(spec, rescaled, initial, old_mole_fraction, new_mole_fraction,
                                  old_path_length, new_path_length, waveunit, units, extra):
    '''
    
    Parameters    
    ----------
    
    spec: Spectrum
    '''
    
#    unit = None    
    apply_slit = False
#    def get_unit():
#        return 'I/I0'

    # case where we recomputed it already (somehow... ex: no_change signaled)
    if 'transmittance' in rescaled:
        if __debug__: printdbg('... rescale: transmittance was scaled already')
        assert 'transmittance' in units
        return rescaled, units, apply_slit
    
    if 'transmittance_noslit' in rescaled:
        apply_slit = True
    else:
        raise NotImplementedError('rescale transmittance not implemented')
#    # Rescale
#    if 'absorbance' in rescaled:
#        if __debug__: printdbg('... rescale: transmittance_noslit T2 = exp(-A2)')
#        absorbance = rescaled['absorbance'] # N and L already scaled
#        transmittance_noslit = exp(-absorbance)           # recalculate
#        unit = get_unit()
#    elif 'transmittance_noslit' in initial:
#        if __debug__: printdbg('... rescale: transmittance_noslit T2 = '+\
#                        'exp( ln(T1) * N2/N1 * L2/L1)')
#        # get transmittance from initial transmittance
#        _, T1 = spec.get('transmittance_noslit', wunit=waveunit, Iunit=units['transmittance_noslit'])
#        
#        
#        # We'll have a problem if the spectrum is optically thick
#        b = (T1 == 0)  # optically thick mask
#        if b.sum()>0 and (new_mole_fraction < old_mole_fraction or 
#                new_path_length < old_path_length):
#            # decreasing mole fractions/ path length could increase the transmittance
#            # but this information was lost in the saturation
#            msg = 'Transmittance is satured. Cant rescale. Please give absorbance'
#            if 'transmittance_noslit' in extra: # cant calculate this one but let it go
#                transmittance_noslit = None
#                if __debug__: printdbg(msg)
#            else:
#                raise ValueError(msg)
#        # Else, just get absorbance
#        absorbance = -ln(T1)
#        absorbance *= new_mole_fraction / old_mole_fraction     # rescale
#        absorbance *= new_path_length / old_path_length         # rescale
#        transmittance_noslit = exp(-absorbance)
#    else:
#        msg = 'Missing data to rescale transmittance. Expected scaled absorbance ({0})'.format(
#                'absorbance' in rescaled)
##        +' or scaled abscoeff ({0}) and true_path_length ({1})'.format(
##                'abscoeff' in rescaled, true_path_length)
#        if 'transmittance_noslit' in extra: # cant calculate this one but let it go
#            transmittance_noslit = None
#            if __debug__: printdbg(msg)
#        else:
#            raise ValueError(msg)
#            
#    # Export rescaled value
#    if transmittance_noslit is not None:
#        rescaled['transmittance_noslit'] = transmittance_noslit
#    if unit is not None:
#        units['transmittance_noslit'] = unit

    return rescaled, units, apply_slit

# ... radiance_noslit
def rescale_radiance_noslit(spec, rescaled, initial, old_mole_fraction, new_mole_fraction,
                             old_path_length, new_path_length, optically_thin, waveunit,
                             units, extra, true_path_length):
    '''
    
    Parameters    
    ----------
    
    spec: Spectrum
    '''
    
    unit = None
    def get_unit(unit_emisscoeff):
        ''' get radiance_noslit unit from emisscoeff unit'''
        if '/cm3' in unit_emisscoeff:
            return unit_emisscoeff.replace('/cm3', '/cm2')
        else:
            return unit_emisscoeff + '*cm'

    # case where we recomputed it already (somehow... ex: no_change signaled)
    if 'radiance_noslit' in rescaled:
        if __debug__: printdbg('... rescale: radiance_noslit was scaled already')
        assert 'radiance_noslit' in units
        return rescaled, units

    # Rescale!
    if 'emisscoeff' in rescaled and true_path_length and optically_thin:
        if __debug__: printdbg('... rescale: radiance_noslit I2 = j2 * L2 '+\
                        '(optically thin)')
        emisscoeff = rescaled['emisscoeff']    # mole_fraction already scaled
        radiance_noslit = emisscoeff*new_path_length      # recalculate
        unit = get_unit(units['emisscoeff'])
        
    elif ('emisscoeff' in rescaled and 'transmittance_noslit' in rescaled
          and 'abscoeff' in rescaled and true_path_length and not optically_thin): # not optically thin
        if __debug__: printdbg('... rescale: radiance_noslit I2 = j2*(1-T2)/k2')
        emisscoeff = rescaled['emisscoeff']    # mole_fraction already scaled
        abscoeff = rescaled['abscoeff']        # mole_fraction already scaled
        transmittance_noslit = rescaled['transmittance_noslit']  # mole_fraction, path_length already scaled
        b = (abscoeff == 0)  # optically thin mask
        radiance_noslit = np.empty_like(emisscoeff)         # calculate
        radiance_noslit[~b] = emisscoeff[~b]/abscoeff[~b]*(1-transmittance_noslit[~b])
        radiance_noslit[b] = emisscoeff[b]*new_path_length # optically thin limit
        unit = get_unit(units['emisscoeff'])
        
    elif ('emisscoeff' in rescaled and 'abscoeff' in rescaled and true_path_length 
          and not optically_thin): # not optically thin
        if __debug__: printdbg('... rescale: radiance_noslit I2 = j2*(1-exp(-k2*L2))/k2')
        emisscoeff = rescaled['emisscoeff']    # mole_fraction already scaled
        abscoeff = rescaled['abscoeff']        # mole_fraction already scaled
        b = (abscoeff == 0)  # optically thin mask
        radiance_noslit = np.empty_like(emisscoeff)         # calculate
        radiance_noslit[~b] = emisscoeff[~b]/abscoeff[~b]*(1-exp(-abscoeff[~b]*new_path_length))
        radiance_noslit[b] = emisscoeff[b]*new_path_length # optically thin limit
        unit = get_unit(units['emisscoeff'])
        
    elif 'radiance_noslit' in initial and optically_thin:
        if __debug__: printdbg('... rescale: radiance_noslit I2 = I1*N2/N1*L2/L1 '+\
                        '(optically thin)')
        _, radiance_noslit = spec.get('radiance_noslit', wunit=waveunit, Iunit=units['radiance_noslit'])
        radiance_noslit *= new_mole_fraction / old_mole_fraction    # rescale
        radiance_noslit *= new_path_length / old_path_length        # rescale
        
    else:
        if optically_thin:
            msg = 'Missing data to rescale radiance_noslit in '+\
                             'optically thin mode. You need at least initial '+\
                             'radiance_noslit ({0}), or scaled emission coefficient ({1}) '.format(
                                     'radiance_noslit' in initial, 'emisscoeff' in rescaled)+\
                             'and true path length ({0}).'.format(true_path_length)
            if 'radiance_noslit' in extra: # cant calculate this one but let it go
                radiance_noslit = None
                if __debug__: printdbg(msg)
            else:
                raise ValueError(msg)
        else:
            msg = 'Missing data to recalculate radiance_noslit. You need at least '+\
                  'scaled emisscoeff ({0}), scaled transmittance_noslit ({1}) '.format(
                          'emisscoeff' in rescaled, 'transmittance_noslit' in rescaled)+\
                  'scaled abscoeff ({0}) and true_path_length ({1}). '.format(
                          'abscoeff' in rescaled, true_path_length)+\
                             'Try in optically thin mode'
            if 'radiance_noslit' in extra:
                radiance_noslit = None
                if __debug__: printdbg(msg)
            else:
                raise ValueError(msg)
            
    # Export rescaled value
    if radiance_noslit is not None:
        rescaled['radiance_noslit'] = radiance_noslit
    if unit is not None:
        units['radiance_noslit'] = unit

    return rescaled, units

# ... radiance
def rescale_radiance(spec, rescaled, initial, old_mole_fraction, new_mole_fraction,
                             old_path_length, new_path_length, optically_thin, waveunit,
                             units, extra, true_path_length):
    '''
    
    Parameters    
    ----------
    
    spec: Spectrum
    '''
    
    apply_slit = False
#    unit = None
#    def get_unit(unit_emisscoeff):
#        if '/cm3' in unit_emisscoeff:
#            return unit_emisscoeff.replace('/cm3', '/cm2')
#        else:
#            return unit_emisscoeff + '*cm'

    # case where we recomputed it already (somehow... ex: no_change signaled)
    if 'radiance' in rescaled:
        if __debug__: printdbg('... rescale: radiance was scaled already')
        assert 'radiance' in units
        return rescaled, units, apply_slit

    # Rescale!
    if 'radiance_noslit' in rescaled:
        apply_slit = True
    else:
        raise NotImplementedError('rescale radiance not implemented yet')
#    if 'emisscoeff' in rescaled and true_path_length and optically_thin:
#        if __debug__: printdbg('... rescale: radiance_noslit I2 = j2 * L2 '+\
#                        '(optically thin)')
#        emisscoeff = rescaled['emisscoeff']    # mole_fraction already scaled
#        radiance_noslit = emisscoeff*new_path_length      # recalculate
#        unit = get_unit(units['emisscoeff'])
#        
#    elif ('emisscoeff' in rescaled and 'transmittance_noslit' in rescaled
#          and 'abscoeff' in rescaled and true_path_length and not optically_thin): # not optically thin
#        if __debug__: printdbg('... rescale: radiance_noslit I2 = j2*(1-T2)/k2')
#        emisscoeff = rescaled['emisscoeff']    # mole_fraction already scaled
#        abscoeff = rescaled['abscoeff']        # mole_fraction already scaled
#        transmittance_noslit = rescaled['transmittance_noslit']  # mole_fraction, path_length already scaled
#        b = (abscoeff == 0)  # optically thin mask
#        radiance_noslit = np.empty_like(emisscoeff)         # calculate
#        radiance_noslit[~b] = emisscoeff[~b]/abscoeff[~b]*(1-transmittance_noslit[~b])
#        radiance_noslit[b] = emisscoeff[b]*new_path_length # optically thin limit
#        unit = get_unit(units['emisscoeff'])
#        
#    elif ('emisscoeff' in rescaled and 'abscoeff' in rescaled and true_path_length 
#          and not optically_thin): # not optically thin
#        if __debug__: printdbg('... rescale: radiance_noslit I2 = j2*(1-exp(-k2*L2))/k2')
#        emisscoeff = rescaled['emisscoeff']    # mole_fraction already scaled
#        abscoeff = rescaled['abscoeff']        # mole_fraction already scaled
#        b = (abscoeff == 0)  # optically thin mask
#        radiance_noslit = np.empty_like(emisscoeff)         # calculate
#        radiance_noslit[~b] = emisscoeff[~b]/abscoeff[~b]*(1-exp(-abscoeff[~b]*new_path_length))
#        radiance_noslit[b] = emisscoeff[b]*new_path_length # optically thin limit
#        unit = get_unit(units['emisscoeff'])
#        
#    elif 'radiance_noslit' in initial and optically_thin:
#        if __debug__: printdbg('... rescale: radiance_noslit I2 = I1*N2/N1*L2/L1 '+\
#                        '(optically thin)')
#        _, radiance_noslit = spec.get('radiance_noslit', wunit=waveunit, Iunit=units['radiance_noslit'])
#        radiance_noslit *= new_mole_fraction / old_mole_fraction    # rescale
#        radiance_noslit *= new_path_length / old_path_length        # rescale
#        
#    else:
#        if optically_thin:
#            msg = 'Missing data to rescale radiance_noslit in '+\
#                             'optically thin mode. You need at least initial '+\
#                             'radiance_noslit ({0}), or scaled emission coefficient ({1}) '.format(
#                                     'radiance_noslit' in initial, 'emisscoeff' in rescaled)+\
#                             'and true path length ({0}).'.format(true_path_length)
#            if 'radiance_noslit' in extra: # cant calculate this one but let it go
#                radiance_noslit = None
#                if __debug__: printdbg(msg)
#            else:
#                raise ValueError(msg)
#        else:
#            msg = 'Missing data to recalculate radiance_noslit. You need at least '+\
#                  'scaled emisscoeff ({0}), scaled transmittance_noslit ({1}) '.format(
#                          'emisscoeff' in rescaled, 'transmittance_noslit' in rescaled)+\
#                  'scaled abscoeff ({0}) and true_path_length ({1}). '.format(
#                          'abscoeff' in rescaled, true_path_length)+\
#                             'Try in optically thin mode'
#            if 'radiance_noslit' in extra:
#                radiance_noslit = None
#                if __debug__: printdbg(msg)
#            else:
#                raise ValueError(msg)
#            
#    # Export rescaled value
#    if radiance_noslit is not None:
#        rescaled['radiance_noslit'] = radiance_noslit
#    if unit is not None:
#        units['radiance_noslit'] = unit
    
    return rescaled, units, apply_slit

# ... emissivity_noslit
def rescale_emissivity_noslit(spec, rescaled, units, extra, true_path_length):
    '''
    
    Parameters    
    ----------
    
    spec: Spectrum
    '''

    # case where we recomputed it already (somehow... ex: no_change signaled)
    if 'emissivity_noslit' in rescaled:
        if __debug__: printdbg('... rescale: emissivity_noslit was scaled already')
        assert 'emissivity_noslit' in units
        return rescaled, units

    # Rescale!
    if 'transmittance_noslit' in rescaled:
        if __debug__: printdbg('... rescale: emissivity_noslit e2 = 1 - T2')
        T2 = rescaled['transmittance_noslit']    # transmittivity already scaled
        emissivity_noslit = 1 - T2                  # recalculate
    else:
        msg = 'transmittance_noslit needed to recompute emissivity_noslit'
        if 'emissivity_noslit' in extra: # cant calculate this one but let it go
            emissivity_noslit = None
            if __debug__: printdbg(msg)
        else:
            raise ValueError(msg)

    # Export rescaled value
    if emissivity_noslit is not None:
        rescaled['emissivity_noslit'] = emissivity_noslit
        units['emissivity_noslit'] = 'eps'

    return rescaled, units

def _recalculate(spec, quantity, new_path_length, old_path_length,
                 new_mole_fraction, old_mole_fraction,
                 true_path_length=True, verbose=True):
    ''' General function to recalculate missing quantities. Used in rescale
    and update

    
    Parameters    
    ----------

    spec: Spectrum
    
    quantity: str
        name of the spectral quantity to recompute. If 'same', only the quantities
        in the Spectrum are recomputed. If 'all', then all quantities that can
        be derived are recomputed. 

    true_path_length: boolean
        if False, only relative rescaling (new/old) is allowed. For instance,
        when you dont know the true path_lenth, rescaling absorbance
        with *= new_length/old_length is fine, but abscoeff*new_length is not
        Default True
    '''
    
    optically_thin = spec.is_optically_thin()
    initial = spec.get_vars()               # quantities initially in spectrum
    if __debug__: printdbg('... rescale: optically_thin: {0}'.format(optically_thin))

    # Check inputs
    assert quantity in CONVOLUTED_QUANTITIES + NON_CONVOLUTED_QUANTITIES + ['all', 'same']
    # ... make sure we're not trying to rescale a Spectrum that has non scalable
    # ... quantities
    if any_in(initial, non_rescalable_keys):
        raise NotImplementedError('Trying to rescale a Spectrum that has non scalable '+\
                                  'quantities: '.format([k for k in initial if k in non_rescalable_keys])+\
                                  'Remove them manually, or implement the scaling method.')

    # Choose which values to recompute (and store them in the list `wanted`)
    # ----------
    if quantity == 'all':                   # quantities to recompute
        wanted = list(initial)  # start from the one we have (that also makes)
                                # sure we dont delete anyone with the final validity
                                # check "everyone is here" 
        greedy = True
    elif quantity == 'same':
        wanted = list(initial)
        greedy = False
    elif isinstance(quantity, string_types):
        wanted = [quantity]
        greedy = False
    else:
        raise ValueError('unexpected type for quantity: expected str, got '+\
                         '{0} ({1})'.format(quantity, type(quantity)))
    rescaled = {}   # quantities rescaled
    
    # in greedy mode ('all'), choose to recompute all parameters that we can 
    extra = []  
    if greedy:
        # ... let's be greedy: recompute all possible quantities. The list of 
        # all spectral quantities is calculated by parsing a tree in get_reachable
        reachable = get_reachable(spec)
        extra = [k for k, v in reachable.items() if v]
    wanted = set(wanted+extra)
    
    # There are two cases: either we are actually rescaling to another length / 
    # mole fraction, or we are just updating() without changing length / mole fraction
    no_change = (new_mole_fraction == old_mole_fraction and new_path_length == old_path_length)
 
    # list of quantities that are needed to recompute what we want
    # ... (we're just analysing how to compute them here, the actual calculation 
    # ... will be done laters)
    try:
        recompute = get_recompute(spec, wanted, no_change, true_path_length=true_path_length)
    except KeyError as err:
        import sys
        print(sys.exc_info())
        raise KeyError('Error in get_recompute (see above). Quantity `{0}` cannot be recomputed '.format(
                err.args[0])+'from available quantities in Spectrum ({0}) with '.format(spec.get_vars())+\
                ' conditions: optically thin ({0}), true_path_length ({1}), equilibrium ({2})'.format(
                     optically_thin, true_path_length, spec.is_at_equilibrium())+\
                     '. Check how your equivalence tree is built: see rescale._build_update_graph()')
    recompute = set(recompute)  # remove duplicates
    
    # Get units 
    units = spec.units.copy()

    # Recompute!
    # ----------
    waveunit = spec.get_waveunit()  # keep all quantities in same waveunit
    apply_slit = False            # if True at the end re-apply slit
    
    # If no_change, just set everyone as rescaled already
    if no_change:
        for k in initial:
            rescaled[k] = spec.get(k)[1]   # note: creates a copy
        
    # Start with abscoeff

    if 'abscoeff' in recompute:
        rescaled, units = rescale_abscoeff(spec, rescaled, initial,     # Todo: remove rescaled = ... Dict is mutable no?
                    old_mole_fraction, new_mole_fraction, old_path_length,
                    waveunit, units, extra, true_path_length)
        
    if spec.is_at_equilibrium():
        assert 'abscoeff' in rescaled
        wavenumber = spec.get_wavenumber('non_convoluted')
        Tgas = spec.conditions['Tgas']
        rescaled, units = _recompute_all_at_equilibrium(spec, rescaled, wavenumber, Tgas, 
                                                 new_path_length, true_path_length,
                                                 units)
        apply_slit = 'radiance' in recompute or 'transmittance' in recompute 
        
    else:
    
        if 'emisscoeff' in recompute:
            rescaled, units = rescale_emisscoeff(spec, rescaled, initial,
                        old_mole_fraction, new_mole_fraction, old_path_length,
                        optically_thin, waveunit, units, extra, true_path_length)
    
        if 'absorbance' in recompute:
            rescaled, units = rescale_absorbance(spec, rescaled, initial,
                        old_mole_fraction, new_mole_fraction, old_path_length,
                        new_path_length, waveunit, units, extra, true_path_length)
    
        if 'transmittance_noslit' in recompute:
            rescaled, units = rescale_transmittance_noslit(spec, rescaled, initial,
                        old_mole_fraction, new_mole_fraction, old_path_length,
                        new_path_length, waveunit, units, extra)
    
        if 'radiance_noslit' in recompute:
            rescaled, units = rescale_radiance_noslit(spec, rescaled, initial,
                        old_mole_fraction, new_mole_fraction, old_path_length,
                        new_path_length, optically_thin, waveunit, units, 
                        extra, true_path_length)
    
        if 'emissivity_noslit' in recompute:
            rescaled, units = rescale_emissivity_noslit(spec, rescaled, units, extra, 
                                                  true_path_length)

        if 'radiance' in recompute:
            rescaled, units, slit_needed = rescale_radiance(spec, rescaled, initial,
                        old_mole_fraction, new_mole_fraction, old_path_length,
                        new_path_length, optically_thin, waveunit, units, 
                        extra, true_path_length)
            apply_slit = apply_slit or slit_needed

        if 'transmittance' in recompute:
            rescaled, units, slit_needed = rescale_transmittance(spec, rescaled, initial,
                        old_mole_fraction, new_mole_fraction, old_path_length,
                        new_path_length, waveunit, units, extra)
            apply_slit = apply_slit or slit_needed
            
    # delete former convoluted value if apply_slit will be used (just to be sure
    # we arent keeping a non rescaled value if something goes wrong)
    if apply_slit:
        for k in spec._q_conv.keys():
            del spec._q_conv[k]
            del spec.units[k]

    # Save (only) the ones that we want, unless we want everything ('greedy')
    for q in rescaled:
        if q in wanted:  # or greedy:
            if q in NON_CONVOLUTED_QUANTITIES:
                spec._q[q] = rescaled[q]
            else:
                spec._q_conv[q] = rescaled[q]
        
    # Update units
    for k, u in units.items():
        spec.units[k] = u

    # Reapply slit if needed
    # TODO: replace with directly convolving with slit stored in conditions
    # TODO: first, add an option to give arrays to apply_slit
    if apply_slit:
        if not ('slit_function' in spec.conditions and 'slit_unit' in spec.conditions
                and 'norm_by' in spec.conditions):
#            if 'transmittance' in extra and 'radiance' in extra:
#                pass  
#            else:
            raise KeyError('Slit is needed to recompute some quantities ({0}) '.format(wanted)+\
                            'but not all conditions are given among slit_function '+\
                            '({0}), slit_unit ({1}) and norm_by ({2})'.format(
                                    'slit_function' in spec.conditions,
                                    'slit_unit' in spec.conditions,
                                    'norm_by' in spec.conditions))
        else:
            slit_function = spec.conditions['slit_function']
            slit_unit = spec.conditions['slit_unit']
            norm_by = spec.conditions['norm_by']
            try:
                shape = spec.conditions['shape']
            except KeyError:
                shape = 'triangular'
            spec.apply_slit(slit_function=slit_function, unit=slit_unit, shape=shape,
                            norm_by=norm_by, verbose=verbose)

    # Final checks

    # ... "everyone is here": check we didnt miss anyone 
    rescaled_list = list(rescaled)
    # add the new quantities added by apply_slit
    rescaled_list = rescaled_list + spec.get_vars('convoluted')
    for q in wanted:
        if not q in rescaled_list:
            raise AssertionError('{0} could not be rescaled as wanted. '.format(q)+\
                                 'The following properties were rescaled: {0}'.format(rescaled_list))
    # ... everyone was added in the Spectrum properly
    final_list = spec.get_vars()
    for q in wanted:
        if not q in final_list:
            raise AssertionError('{0} is not in the final Spectrum. '.format(q)+\
                                 'Rescaled spectrum contains: {0}'.format(final_list))
    # ... "everyone was rescaled": check we didnt scale only part of the spectrum
    for q in initial:
        if not q in rescaled_list:
            raise AssertionError('{0} was initially in the Spectrum but was not '.format(q)+\
                                 'rescaled. This can lead to error. Rescaled spectrum '+\
                                 'contains: {0}'.format(rescaled_list))

def rescale_path_length(spec, new_path_length, old_path_length=None, force=False):
    ''' Rescale spectrum to new path length. Starts from absorption coefficient
    and emission coefficient, and solves the RTE again for the new path length
    Convoluted values (with slit) are dropped in the process.

    
    Parameters    
    ----------

    spec: Spectrum
    
    new_path_length: float
        new path length

    old_path_length: float, or None
        if None, current path length (conditions['path_length']) is used

        
    Other Parameters
    ----------------
    
    force: boolean
        if False, won't allow rescaling to 0 (not to loose information).
        Default False


    Notes
    -----
    
    Implementation:
    
        To deal with all the input cases, we first make a list of what has to
        be recomputed, and what has to be recalculated

    '''

    # Check inputs
    # ----------
    if old_path_length is not None:
        try:
            if spec.conditions['path_length'] != old_path_length:
                warn('path_length ({0}) doesnt match value given in conditions ({1})'.format(
                        old_path_length, spec.conditions['path_length']))
        except KeyError: # path_length not defined
            pass
    else:
        try:
            old_path_length = spec.conditions['path_length']
        except KeyError:
            raise KeyError('path_length has to be defined in conditions (or use'+\
                            ' `from_path_length`)')

    if new_path_length < 0 and not force:
        raise ValueError('path_length cannot be negative')
    if new_path_length == 0 and not force:
        raise ValueError('Rescaling to 0 will loose information. Choose force '\
                         '= True')
    for q in ['transmittance', 'radiance']:
        qns = q+'_noslit'
        qties = spec.get_vars()
        if q in qties and qns not in qties and not force:
            raise KeyError('Cant rescale {0} if {1} not stored'.format(q, qns)+\
                           ' Use force=True to rescale anyway. {0}'.format(q)+\
                           ' will be deleted')

    # Rescale
    _recalculate(spec, 'same', new_path_length, old_path_length, 1, 1)

    # Update conditions
    spec.conditions['path_length'] = new_path_length


def rescale_mole_fraction(spec, new_mole_fraction, old_mole_fraction=None,
            ignore_warnings=False, force=False):
    ''' Update spectrum with new molar fraction
    Convoluted values (with slit) are dropped in the process.

    
    Parameters    
    ----------

    spec: Spectrum
    
    new_mole_fraction: float
        new mole fraction

    old_mole_fraction: float, or None
        if None, current mole fraction (conditions['mole_fraction']) is used

        
    Other Parameters
    ----------------
    
    force: boolean
        if False, won't allow rescaling to 0 (not to loose information).
        Default False


    Notes
    -----
    
    Implementation:
    
        similar to rescale_path_length() but we have to scale abscoeff & emisscoeff
        Note that this is valid only for small changes in mole fractions. Then,
        the change in line broadening becomes significant


    Todo
    -------

    Add warning when too large rescaling
    '''

    # Check inputs
    # ---------
    if old_mole_fraction is not None:
        try:
            if spec.conditions['mole_fraction'] != old_mole_fraction and not ignore_warnings:
                warn('mole_fraction ({0}) doesnt match value given in conditions ({1})'.format(
                        old_mole_fraction, spec.conditions['mole_fraction']))
        except KeyError: # mole fraction not defined
            pass

    else:
        try:
            old_mole_fraction = spec.conditions['mole_fraction']
        except KeyError:
            raise KeyError('mole_fraction has to be defined in conditions (or use'+\
                            ' `from_mole_fraction`)')

    if new_mole_fraction < 0 and not force:
        raise ValueError('mole_fraction cannot be negative')
    if new_mole_fraction == 0 and not force:
        raise ValueError('Rescaling to 0 will loose information. Choose force '\
                         '= True')

    for q in ['transmittance', 'radiance']:
        qns = q+'_noslit'
        qties = spec.get_vars()
        if q in qties and qns not in qties and not force:
            raise KeyError('Cant rescale {0} if {1} not stored.'.format(q, qns)+\
                           '(you need to rescale before applying the slit again) '+\
                           ' Use force=True to rescale anyway, but {0}'.format(q)+\
                           ' will be deleted')

    # Get path length
    if 'path_length' in list(spec.conditions.keys()):
        path_length = spec.conditions['path_length']
        true_path_length = True
    else:
        path_length = 1
        true_path_length = False

    # Rescale
    _recalculate(spec, 'same', path_length, path_length, new_mole_fraction, old_mole_fraction,
                      true_path_length=true_path_length)

    # Update conditions
    spec.conditions['mole_fraction'] = new_mole_fraction



if __name__ == '__main__':

    from radis.test.spectrum.test_rescale import _run_all_tests
    print(('Test rescale.py: ', _run_all_tests(verbose=True)))
    