from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.CrossOver import CrossOver
from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.Individual import Individual
from random import choice, seed

"""
This class implements a type of CrossOver where parents are selected randomly to
produce one son.
"""


class Random_CrossOver(CrossOver):
    def __init__(self, parents_amount):
        super().__init__(parents_amount)

    # Function for establish a seed on random generator
    def set_random_seed(self, n_seed):
        seed(n_seed)

    # Function where the parents are selected
    def select_parents(self, possible_parents):
        selected = []
        for parent in range(self.parents_amount):
            selected.append(choice(possible_parents))
        return selected

    # Function where the crossover is implemented
    def cross(self, parents):
        new_gene = []
        number = 0
        for parent in parents:
            new_gene += parent.get_part(part_number=number,
                                        number_of_breaks=self.parents_amount)
            number += 1
        return Individual(new_gene)
