import numpy as np

from evtol.uav_data import Constants, DesignParameters


def cruise_constraint(constants: Constants, design_parameters: DesignParameters):
    """Returns a function constraining power loading due to cruise.
    Power loading should be higher or equal to the one necessary for cruise
    :return: function describing power loading curve for cruise
    """
    dynamic_pressure = 1 / 2 * constants.air_density * design_parameters.speed_fw_max ** 2
    k = 1 / (np.pi * constants.oswald_efficiency * design_parameters.aspect_ratio)
    cruise_thrust = lambda wing_loading: (
        design_parameters.speed_fw_max / constants.propulsive_efficiency * (
            dynamic_pressure * constants.Cd0 / wing_loading + k / dynamic_pressure * wing_loading))
    return cruise_thrust


def rate_climb_constraint(constants: Constants, design_parameters: DesignParameters):
    """Returns a function constraining power loading and wing-loading due to rate of
    climb in fixed wing mode.
    :return: function describing power loading curve for rate of climb
    """
    k = 1 / (np.pi * constants.oswald_efficiency * design_parameters.aspect_ratio)
    velocity_rate_climb = lambda wing_loading: (2 / constants.air_density * wing_loading * (
        k / (3 * constants.Cd0)) ** 0.5) ** 0.5
    climb_thrust = lambda wing_loading: (
        velocity_rate_climb(wing_loading) / constants.propulsive_efficiency * (
            design_parameters.rate_of_climb_cruise / velocity_rate_climb(
                wing_loading) + 1 / 2 * constants.air_density * velocity_rate_climb(wing_loading)**2 /
            wing_loading *
            constants.Cd0 + k / (
            1 / 2 * constants.air_density * velocity_rate_climb(wing_loading)**2) * wing_loading))
    return climb_thrust


def stall_constraint(constants: Constants, design_parameters: DesignParameters):
    """Returns a function constraining the wing loading.
    The value of the wing loading should be smaller than this.
    """
    return lambda \
            x: 1 / 2 * design_parameters.speed_fw_stall ** 2 * constants.air_density * constants.CL_max
