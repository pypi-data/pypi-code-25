import random
import numpy as np


def simple_mutation(genetic_population, n_task, DNA_length, perturb, prob_mutation, prob_w, is_replace=True):
    for i in range(n_task):
        if random.random() < prob_mutation:
            for _ in range(DNA_length):
                if random.random() < prob_w:
                    choose_place = np.random.choice(np.arange(0, DNA_length))
                    param_shape = genetic_population[i][choose_place].shape
                    for k in range(len(param_shape)):
                        if k == 0:
                            place_str = str(random.randint(0, param_shape[k]-1))
                        else:
                            place_str += ',' + str(random.randint(0, param_shape[k]-1))
                    if is_replace is True:
                        genetic_population[i][choose_place][eval(place_str)] = \
                            np.random.uniform(perturb[choose_place][0], perturb[choose_place][1])
                    else:
                        genetic_population[i][choose_place][eval(place_str)] += \
                            np.sum(np.random.choice([-1, 1])) * np.random.uniform(perturb[choose_place][0], perturb[choose_place][1])

    return genetic_population