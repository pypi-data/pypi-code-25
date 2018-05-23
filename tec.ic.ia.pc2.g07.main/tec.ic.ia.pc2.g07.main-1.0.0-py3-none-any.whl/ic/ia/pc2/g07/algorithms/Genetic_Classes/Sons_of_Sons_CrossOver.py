from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.CrossOver import CrossOver
from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.Individual import Individual
from random import choice,random,seed

"""
This class implements a type of CrossOver where parents are selected randomly to
produce two son and sons have one son.
"""


class Sons_of_Sons_CrossOver(CrossOver):
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
        sons = []
        half = len(parents)//2
        families = [parents[:half], parents[half:]]
        for parents in families:
            if len(parents) == 1:
                sons.append(parents[0])
            else:
                number = 0
                new_gene = []
                for parent in parents:
                    new_gene += parent.get_part(part_number=number,
                                                number_of_breaks=len(parents))
                    number += 1
                new_gene
                sons.append(Individual(new_gene))
        grandson = []
        number = 0
        if random() > 0.5:
            sons = sons[::-1]
        for parent in sons:
            grandson += parent.get_part(part_number=number,
                                        number_of_breaks=len(sons))
            number += 1
        return Individual(grandson)
