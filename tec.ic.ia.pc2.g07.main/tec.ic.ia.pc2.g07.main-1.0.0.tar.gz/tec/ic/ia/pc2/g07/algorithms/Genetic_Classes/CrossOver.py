from abc import ABC, abstractmethod

"""
This class implement an abstract class as a definition of an algorithm.
"""


class CrossOver(ABC):
    def __init__(self, parents_amount):
        self.parents_amount = parents_amount

    # Abstract function where the parents are selected
    @abstractmethod
    def select_parents(self, possible_parents):
        pass

    # Abstract function where the crossover is implemented
    @abstractmethod
    def cross(self, parents):
        pass
