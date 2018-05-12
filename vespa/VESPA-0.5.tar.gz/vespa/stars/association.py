from __future__ import print_function, division
import numpy as np
from scipy.stats import gaussian_kde

from .utils import rho_bg
from ..orbits import OrbitPopulation

def rsky_lhood(mod, N=1e5, mu_logp=np.log10(250), sig_logp=2.3, min_period=1.,
                beta_a=0.8, beta_b=2.0, max_ecc=0.9,
                rho_5=0.05, rho_20=0.005, recalc=False):
    """
    Calculates L(rsky | {bound OR unbound}), depending on which is relevant.

    Only works for two obs_leaf_nodes.

    If bound binary, then this generates an orbit population according to 
    mu_logp, sig_logp.  Default parameters correspond to Duchene & Kraus 
    characterization of the Raghavan period distribution.

    If unbound, then calculates based on BG star density, 
    parameterized by rho_5, rho_20
    """
    if len(mod.obs.obs_leaf_nodes) != 2:
        raise NotImplementedError('rsky_lhood currently only implemented for 2-star system.')

    o1, o2 = mod.obs.obs_leaf_nodes
    separation = o1.distance(o2)
    if len(mod.obs.systems)==1:
        # Bound binary.  Use OrbitPopulation
        samples = mod.random_samples(N)
        period = 10**(np.random.normal(mu_logp, sig_logp, size=int(N))) * 365.25
        bad = period < min_period
        nbad = bad.sum()
        while nbad > 0:
            period[bad] = 10**(np.random.normal(mu_logp, sig_logp, size=int(nbad))) * 365.25
            bad = period < min_period
            nbad = bad.sum()

        ecc = np.random.beta(beta_a, beta_b, int(N))
        bad = ecc > max_ecc
        nbad = bad.sum()
        while nbad > 0:
            ecc[bad] = np.random.beta(beta_a, beta_b, nbad)
            bad = ecc > max_ecc
            nbad = bad.sum()

        orbpop = OrbitPopulation(samples['mass_0_0'], 
                                       samples['mass_0_1'],
                                       period, ecc)
        rsky = orbpop.Rsky.value / samples['distance_0'].values # orbpop.Rsky is projected AU
        log_kde = gaussian_kde(np.log(rsky))
        pdf = lambda r: 1./r * log_kde(np.log(r))[0]
        return pdf(separation)
    elif len(mod.obs.systems)==2:
        rho = rho_bg(mod.coords.galactic.b.deg, rho_5=rho_5, rho_20=rho_20)
        return 2*np.pi*separation*rho
    else:
        raise ValueError('Can only have one or two systems in StarModel: {}'.format(mod.obs.systems))

def prob_associated(mod_bound, mod_unbound, **kwargs):
    L1 = rsky_lhood(mod_bound, **kwargs)
    L2 = rsky_lhood(mod_unbound, **kwargs)
    return L1*0.5 / (L1*0.5 + L2)

