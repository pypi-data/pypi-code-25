#!/usr/bin/env python

# <examples/doc_builtinmodels_nistgauss.py>
import matplotlib.pyplot as plt
import numpy as np

from lmfit.models import ExponentialModel, GaussianModel

dat = np.loadtxt('NIST_Gauss2.dat')
x = dat[:, 1]
y = dat[:, 0]

exp_mod = ExponentialModel(prefix='exp_')
pars = exp_mod.guess(y, x=x)

gauss1 = GaussianModel(prefix='g1_')
pars.update(gauss1.make_params())

pars['g1_center'].set(105, min=75, max=125)
pars['g1_sigma'].set(15, min=3)
pars['g1_amplitude'].set(2000, min=10)

gauss2 = GaussianModel(prefix='g2_')

pars.update(gauss2.make_params())

pars['g2_center'].set(155, min=125, max=175)
pars['g2_sigma'].set(15, min=3)
pars['g2_amplitude'].set(2000, min=10)

mod = gauss1 + gauss2 + exp_mod

init = mod.eval(pars, x=x)

out = mod.fit(y, pars, x=x)
print(out.fit_report(min_correl=0.5))

plot_components = False

plt.plot(x, y, 'b')
plt.plot(x, init, 'k--')
plt.plot(x, out.best_fit, 'r-')

if plot_components:
    comps = out.eval_components(x=x)
    plt.plot(x, comps['g1_'], 'b--')
    plt.plot(x, comps['g2_'], 'b--')
    plt.plot(x, comps['exp_'], 'k--')

plt.show()
# <end examples/doc_builtinmodels_nistgauss.py>

#
import numpy as np
import matplotlib.pyplot as plt
from lmfit.models import GaussianModel

y, bin_edges = np.histogram(Density, bins=np.logspace(np.log10(MIN), np.log10(MAX), 32))

x = np.log((bin_edges[:-1] + bin_edges[1:])/2.0)



model = GaussianModel(prefix='g1_') + GaussianModel(prefix='g2_') + GaussianModel(prefix='g3_')

# initial values for parameters

params = model.make_params(g1_amplitude=60, g1_center=-1.0, g1_sigma=1,
                           g2_amplitude=30, g2_center= 0.0, g1_sigma=1,
                           g2_amplitude=10, g2_center= 1.0, g1_sigma=1)

params['g1_amplitude'].min = 0
params['g2_amplitude'].min = 0
params['g3_amplitude'].min = 0

params['g1_cen'].max = 0

params['g2_cen'].min = -1.0
params['g2_cen'].max = 1.0

params['g3_cen'].min = 0

result = model.fit(y, params, x=x)

print(result.fit_report())


comps = result.eval_components(result.params, x=x)


plt.plot(x, y, label='data')
plt.plot(x, result.best_fit, label='best fit')

plt.plot(x, comps['g1_'], label='gaussian1')
plt.plot(x, comps['g2_'], label='gaussian2')
plt.plot(x, comps['g3_'], label='gaussian3')
# other plt methods for axes and labels
plt.show()
