import julia
#from subprocess import run, PIPE
from power_models_wrapper.formulation_type import FormulationType

class RemoteOffGrid:

    def __init__(self):
        #pass
        self.__julia_object = julia.Julia()
        self.__julia_object.using("RemoteOffGridMicrogrids")

    def run(self, input_data_file_path):

        julia_code = "run_model(\"" + input_data_file_path + "\")"

        #print("julia_code: %s" % (julia_code))

        result = self.__julia_object.eval(julia_code)

        #julia_code = "using RemoteOffGridMicrogrids; " + "result = run_model(\"" + input_data_file_path + "\"); " + " println(result)"

        #result = run(["julia", "-e", julia_code], stdout = PIPE)

        return result
