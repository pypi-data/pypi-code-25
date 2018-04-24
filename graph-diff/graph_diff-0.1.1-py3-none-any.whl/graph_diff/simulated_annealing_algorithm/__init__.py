"""
Module simulated_annealing contains realization of Simulated Annealing Algorithm
for graph difference problem.
It is an heuristic algorithm so exact result is not guaranteed.
Complexity of the method is O(NI * V_1), where
- NI - number of iterations
- NA - number of agents (number of independent route constructors)
- V_1 - number of nodes in the first graph
TODO: add references
TODO: add accuracy evaluation
"""

from .algorithm import Algorithm as SimAnnealAlgorithm
