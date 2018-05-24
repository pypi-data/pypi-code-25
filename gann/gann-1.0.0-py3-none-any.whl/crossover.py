import random
import numpy as np


def one_point_crossover(genetic_population, pc, n_task):
    population_copy = genetic_population.copy()
    DNA_length = len(genetic_population)
    for i in range(0, n_task, 2):
        if i == n_task-1:
            break
        if random.random() < pc:
            cro_point = np.random.choice(np.arange(0, DNA_length-1, 2))
            genetic_population[i][:cro_point] = population_copy[i][:cro_point]
            genetic_population[i][cro_point:] = population_copy[i+1][cro_point:]
            genetic_population[i+1][:cro_point] = population_copy[i+1][:cro_point]
            genetic_population[i+1][:cro_point] = population_copy[i+1][:cro_point]
            genetic_population[i+1][cro_point:] = population_copy[i][cro_point:]
    return genetic_population