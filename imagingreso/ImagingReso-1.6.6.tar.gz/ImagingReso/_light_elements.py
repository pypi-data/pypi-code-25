from ImagingReso.resonance import Resonance
import pprint

_energy_min = 100
_energy_max = 10000000
_energy_step = 5

_layer_1 = 'K'
_thickness_1 = 1  # mm
# _density_1 = 8  # g/cm3 deviated due to porosity

_layer_2 = 'N'
_thickness_2 = 1  # mm

_layer_3 = 'C'
_thickness_3 = 1  # mm
# _density_3 = 0.7875  # g/cm3

o_reso = Resonance(energy_min=_energy_min, energy_max=_energy_max, energy_step=_energy_step)
o_reso.add_layer(formula=_layer_1, thickness=_thickness_1)
o_reso.add_layer(formula=_layer_2, thickness=_thickness_2)
o_reso.add_layer(formula=_layer_3, thickness=_thickness_3)

pprint.pprint(o_reso.stack)

o_reso.plot(x_axis='time', y_axis='sigma',
            mixed=False, all_elements=True,
            x_in_log=True, y_in_log=True,
            time_unit='ns', source_to_detector_m=16)
