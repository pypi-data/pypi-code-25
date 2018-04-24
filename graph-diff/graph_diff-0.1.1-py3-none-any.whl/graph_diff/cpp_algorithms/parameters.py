"""
Parameters defined in module
"""
from collections import defaultdict

# Defines if cpp source will be recompiled
# each time algorithm (AlgorithmRunner.construct_diff) is run.
RECOMPILE = True

# .cpp file that will be compiled
FILENAME = 'main.cpp'

# Executable name that will be produced and supposedly used later
EXE_FILENAME = 'main'

# Set of class names of corresponding algorithms that have cpp realization.
# Any of listed names may be used in AlgorithmRunner and AlgorithmCompiler
# methods construct_diff and compile respectively. As well as that these methods
# are preferred to be used as compile_{} and {}_construct_diff with {} as snake_case version
# of the class name of the algorithm to be used.
# For example: compile_baseline_algorithm and baseline_algorithm_construct_diff.
SUPPORTED_ALGORITHMS = {'BaselineAlgorithm',
                        'BaselineWithChopAlgorithm',
                        'BaselineAlgorithmOmp',
                        'BaselineWithChopAlgorithmOmp',
                        'AntAlgorithm',
                        'LinAntAlgorithm'}

ALGORITHMS_INCLUDE = {'AntAlgorithm': 'graph_diff::algorithm::AntAlgorithm<CubedPathfinder>',
                      'LinAntAlgorithm': 'graph_diff::algorithm::AntAlgorithm<LinearPathfinder>'}

ALGORITHMS_FLAGS = defaultdict(list)
ALGORITHMS_FLAGS['BaselineAlgorithmOmp'] = ['-Xpreprocessor', '-fopenmp', '-lomp']
ALGORITHMS_FLAGS['BaselineWithChopAlgorithmOmp'] = ['-Xpreprocessor', '-fopenmp', '-lomp']

# Compiler to be used for pure cpp realizations of algorithms
CPP_COMPILER = 'g++'

# Flag of optimization used by compiler
CPP_OPTIMIZATION = '-o3'

# Cpp standard used for compilation.
CPP_STANDARD = '-std=c++1z'
