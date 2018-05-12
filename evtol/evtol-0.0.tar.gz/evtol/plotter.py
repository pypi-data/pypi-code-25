from evtol.constraint_analysis import cruise_constraint, rate_climb_constraint, stall_constraint
from evtol.uav_data import Constants, DesignParameters
import numpy as np
import matplotlib.pyplot as plt

def wing_loading_diagram(wing_loading_domain, constants: Constants, design_parameters:
DesignParameters):
    cruise_curve = cruise_constraint(constants, design_parameters)(wing_loading_domain)
    rate_climb_curve = rate_climb_constraint(constants, design_parameters)(wing_loading_domain)
    stall_curve = stall_constraint(constants, design_parameters)(wing_loading_domain)
    plt.plot(wing_loading_domain, cruise_curve)
    plt.plot(wing_loading_domain, rate_climb_curve)
    plt.axvline(x=stall_curve)
    plt.legend(['cruise', 'roc', 'stall'])
    plt.show()

