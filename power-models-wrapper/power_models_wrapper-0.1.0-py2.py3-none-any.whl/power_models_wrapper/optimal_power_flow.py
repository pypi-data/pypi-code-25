import julia
from power_models_wrapper.formulation_type import FormulationType

class OptimalPowerFlow:

    def __init__(self):
        self.__julia_object = julia.Julia()
        self.__julia_object.using('PowerModels')

    def run(self, input_matlab_data_file_path, formulation_type = FormulationType.ac):

        #julia_code = 'PowerModels.parse_file("' + input_matlab_data_file_path + '")'
        # TODO: Initial implementation of using PowerModels run method, using hardcoded solver:
        self.__julia_object.using('Ipopt')
        julia_code = self.__get_julia_run_method_name(formulation_type) + '("' + input_matlab_data_file_path + '", IpoptSolver())'

        result = self.__julia_object.eval(julia_code)

        return result

    def __get_julia_run_method_name(self, formulation_type):
        return "run_%(formulation_type)s_opf" % {'formulation_type':formulation_type.name}
