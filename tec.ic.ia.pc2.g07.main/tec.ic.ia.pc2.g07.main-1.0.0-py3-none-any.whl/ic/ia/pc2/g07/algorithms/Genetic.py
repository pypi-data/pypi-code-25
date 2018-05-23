from tec.ic.ia.pc2.g07.algorithms.Algorithm import Algorithm
from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.Individual import Individual
from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.CrossOver import CrossOver
from random import random, choice, randint, seed
import os
"""
This class implements a genetic algorithm to solve a path-finding problem.
"""


class Genetic(Algorithm):
    def __init__(self, board, direction, number_individuals, number_generations, crossover, mutation_rate):
        super().__init__(board)
        self.rows_in_board = 0
        self.cols_in_board = 0
        self.direction = direction
        self.number_individuals = number_individuals
        self.number_generations = number_generations
        self.crossover = crossover
        self.mutation_rate = mutation_rate

    # Function for establish a seed on random generator
    def set_random_seed(self, n_seed):
        seed(n_seed)

    # Function to produce every individual same as the board
    def first_birth(self, template, amount):
        gene = []
        for row in template:
            gene += row

        # Population
        return [Individual(gene) for i in range(amount)]

    # Function to mutate the population given a mutation rate.
    def mutate_population(self, population, mutation_rate):
        max_index = len(population[0].gene)-1
        possibilities = [">", "<", "V", "A", " "]
        new_individuals = []
        for individual in population:
            if random() <= mutation_rate/100:
                field_index = randint(0, max_index)
                if individual.gene[field_index] not in ["C", "Z"]:
                    new_gene = individual.gene[:]
                    poss = possibilities[:]
                    poss.remove(individual.gene[field_index])
                    new_gene[field_index] = choice(poss)
                    new_individuals.append(new_gene)
        population += [Individual(gene) for gene in new_individuals]

    # Function to check a coordinate is aceptable (in-borders of the board)
    def is_in_board(self, x, y):
        if x < 0 or y < 0 or x >= self.rows_in_board or y >= self.cols_in_board:
            return False
        return True

    # Function to get information at walking through the board
    def walk_trough_board(self, board, rabbit, max_movements):
        directions = [[0, -1], [0, 1], [-1, 0], [1, 0]]
        dir_names = ["izquierda", "derecha", "arriba", "abajo"]
        signals = ["<", ">", "A", "V"]
        contra = [">", "<", "V", "A"]
        selected_direction = directions[dir_names.index(self.direction)]
        movements = 0
        carrots_eaten = []
        used_signals = []
        previous_signal = signals[dir_names.index(self.direction)]
        has_signals_contra = False
        carrots_since = 0
        previous_useful_signal = []
        while True:
            if movements == max_movements:
                return movements, len(carrots_eaten), len(used_signals), has_signals_contra

            step = [rabbit[0]+selected_direction[0],
                    rabbit[1]+selected_direction[1]]
            if not self.is_in_board(step[0], step[1]):
                if carrots_since != 0 and previous_useful_signal != []:
                    used_signals.append(previous_useful_signal)
                return movements, len(carrots_eaten), len(used_signals), has_signals_contra

            movements += 1
            if board[step[0]][step[1]] == 'Z' and step not in carrots_eaten:
                carrots_eaten.append(step[:])
                carrots_since += 1
            elif board[step[0]][step[1]] in signals:
                if selected_direction != directions[signals.index(board[step[0]][step[1]])] and step not in used_signals:
                    if carrots_since != 0 and previous_useful_signal != []:
                        used_signals.append(previous_useful_signal)
                        carrots_since = 0
                    if previous_signal == contra[signals.index(board[step[0]][step[1]])]:
                        has_signals_contra = True
                    else:
                        previous_useful_signal = step[:]
                selected_direction = directions[signals.index(
                    board[step[0]][step[1]])]
                previous_signal = board[step[0]][step[1]]

            rabbit = step[:]

    # Function to calculate fitness using information of the walk through the board
    def calculate_fitness(self, population):
        carrots = population[0].gene.count("Z")
        rabbit = population[0].gene.index("C")
        rabbit = [rabbit//self.cols_in_board %
                  self.rows_in_board, rabbit % self.cols_in_board]
        max_movements = self.rows_in_board*self.cols_in_board
        fitness = 0
        for individual in population:
            board = individual.gene_as_board(self.cols_in_board)
            movements, carrots_eaten, useful_signals, has_signals_contra = self.walk_trough_board(
                board, rabbit, max_movements)

            if has_signals_contra:
                fitness -= 1000
            if movements == max_movements:
                fitness -= 1000
            if individual.amount_of_signals() == 0 and carrots != carrots_eaten:
                fitness -= 50
            fitness -= (50 * (individual.amount_of_signals() - useful_signals))
            fitness += carrots_eaten * 100
            fitness -= (carrots - carrots_eaten) * 50
            fitness += 3 * useful_signals
            fitness += movements * 5

            individual.fitness = fitness
            fitness = 0

    # Function to print the results and save them in a file
    def print_and_save(self, population, generation):
        basedir = os.path.dirname(
            "Results_GA\\"+self.direction+"\\%05d\\00001.txt" % (generation,))
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        print("\nGENERACION: %05d" % (generation,))
        num = 1
        for individual in population:
            print("INDIVIDUO %05d APTITUD:" % (num,) + str(individual.fitness))
            with open("Results_GA\\"+self.direction+"\\%05d\\%05d.txt" % (generation, num,), "w") as file:
                for row in individual.board:
                    file.writelines(row)
                    file.write("\n")
            num += 1

    # Function that calls the above functions
    def execute(self):
        print("\nDeleting old results...")
        self.remove_last_results("Results_GA\\"+self.direction)
        # Variables to save files
        self.rows_in_board = len(self.board)
        self.cols_in_board = len(self.board[0])

        # Create original individuals
        population = self.first_birth(
            template=self.board, amount=self.number_individuals)

        # Reproduce for generations
        for generation in range(self.number_generations):
            old_population = population[:]
            for i in range(self.number_individuals):
                # Fathers Selection
                parents = self.crossover.select_parents(old_population)
                # Reproduction
                new_individual = self.crossover.cross(parents)
                # Integration to the society
                population.append(new_individual)

            # Mutation
            self.mutate_population(population, self.mutation_rate)

            # Calculate population's fitness
            self.calculate_fitness(population)

            # Sort popoulation by fitness
            population.sort(key=lambda x: x.fitness, reverse=True)

            # Selection of Next Generation
            population = population[:self.number_individuals]

            # Print to console and save file
            self.print_and_save(population, generation+1)
