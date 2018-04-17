import os
import re

from oplus.configuration import CONF




class MTDError(Exception):
    pass


class MTD:
    def __init__(self, path, logger_name=None, encoding=None):
        if not os.path.isfile(path):
            raise MTDError("No file at given path: '%s'." % path)
        self._path = path
        self._logger_name = logger_name
        self._encoding = encoding

        self._variables_d, self._meters_d = self._parse()

    def _parse(self):
        variables_d = {}  # {ref: object, ...}
        meters_d = {}  # {ref: object, ...}

        output_l, current, current_s = None, None, None
        var_pattern = r"^ Meters for (\d*),([^\[\]]*) \[([\w\d]*)\]$"
        meter_pattern = r"^ For Meter=([^\[\]]*) \[([\w\d]*)],(.*)$"

        # build variables and meters
        with open(self._path, "r", encoding=CONF.encoding if self._encoding is None else self._encoding) as f:
            for line_s in f:
                if line_s == "\n":
                    if output_l is None:  # initialize
                        output_l = []
                    else:
                        output_l.append([current, current_s])
                    current, current_s = None, ""
                    continue
                if current is None:
                    # try variable
                    match = re.search(var_pattern, line_s)
                    if match is not None:
                        current = Variable(match.group(2), int(match.group(1)), match.group(3))
                        variables_d[current.ref] = current
                    else:
                        match = re.search(meter_pattern, line_s)
                        if match is None:
                            raise MTDError("Line was not parsed correctly: '%s'." % line_s)
                        kwargs = {}
                        for kv in line_s.split(",")[:-1]:
                            k, v = kv.split("=")
                            kwargs[k] = v
                        current = Meter(match.group(1), match.group(2), **kwargs)
                        meters_d[current.ref] = current
                else:
                    current_s += line_s

        # create links
        meter_pattern = r"^  OnMeter=([^\[\]]*) \[[\w\d]*\]$"
        var_pattern = r"^  (.*)$"
        for k, v in output_l:
            if isinstance(k, Variable):
                for v_s in v.split("\n")[:-1]:
                    match = re.search(meter_pattern, v_s)
                    if match is None:
                        raise MTDError("Meter pattern not parsed: '%s'." % v_s)
                    k.link_meter(meters_d[match.group(1)])
            else:
                for v_s in v.split("\n")[:-1]:
                    match = re.search(var_pattern, v_s)
                    if match is None:
                        raise MTDError("Variable pattern not parsed: '%s'." % v_s)
                    k.link_variable(variables_d[match.group(1)])

        return variables_d, meters_d

    def get_variable_refs(self, meter_ref):
        return [v.ref for v in self._meters_d[meter_ref].variables_l]

    def has_meter(self, meter_ref):
        return meter_ref in self._meters_d


class Meter:
    def __init__(self, ref, unit, **kwargs):
        self.ref = ref
        self.unit = unit
        self.kwargs = kwargs

        self.variables_l = []

    def link_variable(self, variable):
        if variable in self.variables_l:
            raise MTDError("Variable already linked.")
        self.variables_l.append(variable)


class Variable:
    def __init__(self, ref, variable_id, unit):
        self.ref = ref
        self.variable_id = variable_id
        self.unit = unit

        self.meters_l = []

    def link_meter(self, meter):
        if meter in self.meters_l:
            raise MTDError("Meter already linked.")
        self.meters_l = []

if __name__ == "__main__":
    mtd = MTD(r"C:\Users\Geoffroy\Desktop\simul_dir\rs_2013-opt_chicago.mtd")

    # print("VARIABLES")
    # for k in sorted(mtd._variables_d):
    #     print("'%s'" % k)
    #
    # print()
    # print("METERS")
    # for k in sorted(mtd._meters_d):
    #     print("'%s'" % k)

    # print(mtd.get_variable_refs("CH4:Facility"))
    meters_structure = [
        # "Heating", "Cooling", "InteriorLights", "ExteriorLights", "InteriorEquipment", "ExteriorEquipment", "Fans",
        # "Pumps", "HeatRejection", "Humidification", "HeatRecovery", "WaterSystems", "Refrigeration", "Generators"
        ["Electricity", ["Heating", "Cooling", "InteriorLights", "ExteriorLights", "InteriorEquipment", "Fans",
                         "HeatRecovery"]],
        ["Gas", ["Heating", "WaterSystems"]],
        ["Water", ["WaterSystems"]]
    ]
    for source, uses_l in meters_structure:
        for use in uses_l:
            meter_ref = "%s:%s" % (use, source)
            if not mtd.has_meter(meter_ref):
                print("ERROR: '%s' not found." % meter_ref)