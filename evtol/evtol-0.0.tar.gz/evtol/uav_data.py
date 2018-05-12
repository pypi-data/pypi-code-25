class MissionProfile(object):
    def __init__(self):
        self.fw_range = None
        self.fw_loiter_time = None
        self.vtol_hover_time = None
        self.vtol_climb_time = None

    def is_complete(self):
        for key, value in vars(self).items():
            if value == None:
                raise AttributeError("Not all mission profile parameters set. Missing: {}. Quitting.".format(key))


class Constants(object):
    def __init__(self):
        
        self.air_density = 1.225
        self.gravitational_acc = 9.81
        
        self.Cd0 = 0.04
        self.CL_max = 1.0
        self.oswald_efficiency = 0.7
        self.propulsive_efficiency = 0.7
        self.projected_area_fraction = 1.4
        self.gain_merit = None
        
        self.specific_energy_capacity = None
        self.battery_voltage = None
        self.electric_efficiency = None
        self.battery_efficiency = None
        self.fraction_usable_battery_capacity = None
        
        self.motor_type_vtol = None
        self.motor_type_fw = None
        self.number_of_propellers_vtol = None
        self.number_of_propellers_fw = None
        self.number_of_blades_vtol = None
        self.number_of_blades_fw = None
        self.propeller_type_fw = None
        self.propeller_type_vtol = None

        self.fw_range = None
        self.fw_loiter_time = None
        self.vtol_hover_time = None
        self.climb_height_vtol = 150
        self.number_of_climbs_vtol = 5

        self.mass_payload = None
        self.mass_fraction_structures = 0.4
        self.mass_fraction_subsystems = 0.15
        self.mass_fraction_avionics = 0.05
        self.propulsion_installation_coefficient = 1.0

    def is_complete(self):
        for key, value in vars(self).items():
            if value == None:
                raise AttributeError("Not all constants set. Missing: {}. Quitting.".format(key))

#TODO: Setters for AR/span/chord/area etc.
class DesignParameters(object):
    def __init__(self):
        self.wing_span = None
        self.aspect_ratio = None 
        self.wing_loading = None
        self.power_over_weight = None
        self.rate_of_climb_cruise = None
        self.rate_of_climb_vtol = None
        self.speed_fw_max = None
        self.speed_fw_stall = None
        self.diameter_prop_fw = None
        self.diameter_prop_vtol = None
        self.mass_takeoff = None

    def vectorize(self):
        """Vectorizes the design parameters
        :return: list containing parameters to be optimized
        """
        return list(self.__dict__.keys()), list(self.__dict__.values())

    def is_complete(self):
        for key, value in vars(self).items():
            if value is None:
                raise AttributeError("Not all design parameters set. Missing: {}. Quitting.".format(key))
