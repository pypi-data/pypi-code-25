import os
import sys

import stringcase

from graph_diff.cpp_algorithms.parameters import SUPPORTED_ALGORITHMS


class AlgorithmImporter:
    """Class for importing cpp algorithms as python module"""
    def __init__(self):
        sys.path.append(self.__current_dir())

        if not os.path.isfile(os.path.join(self.__current_dir(), 'cpp_algorithms.cpp')):
            self.__print_importer()

        # noinspection PyUnresolvedReferences
        import cppimport.import_hook

        # noinspection PyUnresolvedReferences
        import cpp_algorithms
        # due to cppimport.import_hook and __location__
        # we import cpp_algorithms.cpp and are able to use it

        self.module = cpp_algorithms

        sys.path.pop()

    def __current_dir(self):
        return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    def __print_importer(self):
        algorithms = [f'm.def("{stringcase.snakecase(alg_name)}", &algorithm<size_t, {alg_name}>);'
                      for alg_name in SUPPORTED_ALGORITHMS]
        algorithms = '\n    '.join(algorithms)

        printed = f"""/*cppimport
<%
setup_pybind11(cfg)
cfg['compiler_args'] = ['-std=c++1z', '-stdlib=libc++']
cfg['compiler_args'] += ['-Xpreprocessor', '-fopenmp']
cfg['linker_args'] = ['-lomp']
cfg['include_dirs'] = ['ant_algorithm', 'baseline_algorithm']
cfg['dependencies'] = ['baseline_algorithms_using.hpp', 
                       'baseline_algorithms.hpp', 
                       'baseline_algorithms/baseline_algorithm.hpp',
                       'baseline_algorithms/baseline_algorithm_omp.hpp',
                       'baseline_algorithms/baseline_with_chop_algorithm.hpp',
                       'baseline_algorithms/baseline_with_chop_algorithm_omp.hpp']
cfg['dependencies'] += ['ant_algorithm/ant_parameters.hpp', 
                        'ant_algorithm/ant_algorithm.hpp',
                        'ant_algorithm/graph_stat.hpp',
                        'ant_algorithm/pathfinder.hpp',
                        'ant_algorithm/pheromon_table.hpp',
                        'ant_algorithm/utils.hpp']
%>
*/
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <iostream>

#include "graph.hpp"
#include "baseline_algorithms_using.hpp"
#include "ant_algorithm/ant_algorithm.hpp"
using graph_diff::algorithm::AntAlgorithm;

template <typename T> using node = std::pair<T, size_t>;

template <typename T, typename Algorithm>
auto algorithm(std::vector<node<size_t>> nodes1,
               std::vector<std::vector<size_t>> adjacent_list1,
               std::vector<node<size_t>> nodes2,
               std::vector<std::vector<size_t>> adjacent_list2) {{
    auto graph1 = graph_diff::graph::Graph<T>(nodes1, adjacent_list1);
    auto graph2 = graph_diff::graph::Graph<T>(nodes2, adjacent_list2);

    auto best_choice = Algorithm().construct_diff(graph1, graph2);

    return best_choice;
}}
"""

        file = open(os.path.join(self.__current_dir(), 'cpp_algorithms.cpp'), 'w')
        print(printed, file=file)
