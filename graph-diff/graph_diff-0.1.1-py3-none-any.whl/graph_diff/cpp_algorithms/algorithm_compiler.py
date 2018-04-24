import os
import subprocess

from graph_diff.cpp_algorithms import parameters
from graph_diff.cpp_algorithms.decorators import clone_method
from graph_diff.cpp_algorithms.parameters import ALGORITHMS_INCLUDE


@clone_method('compile', *parameters.SUPPORTED_ALGORITHMS)
class AlgorithmCompiler:
    """Class for compiling cpp source to get certain algorithms"""

    FILENAME = parameters.FILENAME
    EXE_FILENAME = parameters.EXE_FILENAME
    SUPPORTED_ALGORITHMS = parameters.SUPPORTED_ALGORITHMS
    ALGORITHMS_FLAGS = parameters.ALGORITHMS_FLAGS
    CPP_COMPILER = parameters.CPP_COMPILER
    CPP_OPTIMIZATION = parameters.CPP_OPTIMIZATION
    CPP_STANDARD = parameters.CPP_STANDARD

    def compile(self, algorithm: str) -> str:
        """
        Compiles cpp source with algorithm defined.
        Can (and to preferred) to be ran as
        compile_{snake_case_version_of_algorithm_name}.

        For example:
            compiler.compile_baseline_algorithm()

        :param algorithm:   cpp class name of the corresponding algorithm
        :return:            path to the executable
        """
        assert algorithm in self.SUPPORTED_ALGORITHMS

        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        filename = os.path.join(__location__, self.FILENAME)
        exe_filename = os.path.join(__location__, self.EXE_FILENAME)

        cmd = [self.CPP_COMPILER,
               self.CPP_OPTIMIZATION,
               self.CPP_STANDARD,
               filename,
               *self.ALGORITHMS_FLAGS[algorithm],
               '-o', exe_filename,
               '-D', f'Algorithm={ALGORITHMS_INCLUDE.get(algorithm, algorithm)}']
        p = subprocess.Popen(cmd)
        p.wait()

        return exe_filename
