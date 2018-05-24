import numpy as np


def sorting_selection(population_id, fitness, n_task):
    arg_f = fitness.copy()
    arg = np.argsort(arg_f)
    for i in range(len(arg)):
        arg_f[arg[i]] = i
    new_population_id = np.random.choice(population_id, (n_task,), p=arg_f/np.sum(arg_f))
    return new_population_id