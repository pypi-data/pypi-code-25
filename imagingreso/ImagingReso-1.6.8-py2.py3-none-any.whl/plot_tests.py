from ImagingReso.resonance import Resonance
import matplotlib.pyplot as plt

o_reso = Resonance(energy_max=300, energy_min=1, energy_step=0.01)

o_reso.add_layer(formula='Ag', thickness=1)

o_reso.plot(fmt='o')

plt.show()