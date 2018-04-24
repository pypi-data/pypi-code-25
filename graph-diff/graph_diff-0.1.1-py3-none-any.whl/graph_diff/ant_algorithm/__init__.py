"""
Module ant_algorithm contains realization of Ant Algorithm
for graph difference problem.
It is an heuristic algorithm so exact result is not guaranteed.
Complexity of the method is O(NI * (NA * E_1 + V_1) * V_2), where
- NI - number of iterations
- NA - number of agents (number of independent route constructors)
- E_1 - number of edges in the first graph
- V_1 - number of nodes in the first graph
- V_2 - number of nodes in the second graph
TODO: add references
TODO: add accuracy evaluation
"""

from .algorithm import Algorithm as AntAlgorithm
