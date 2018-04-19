from scoop import futures, logger
from parallel_ga_processing.geneticAlgorithms import CoarseGrainedBase


def run_coarse_grained_ga(population_size, chromosome_size,
                          number_of_generations,
                          neighbourhood_size, server_user, server_password, server_ip_addr,
                          num_of_migrants, fitness):
    ins = CoarseGrainedBase(population_size=population_size, chromosome_size=chromosome_size,
                            number_of_generations=number_of_generations,
                            neighbourhood_size=neighbourhood_size,
                            num_of_migrants=num_of_migrants, fitness=fitness)

    x, y = population_size

    server_users = make_one_for_each(server_user, x * y)
    server_passwords = make_one_for_each(server_password, x * y)
    server_ip_addrs = make_one_for_each(server_ip_addr, x * y)

    populations = ins.initialize_population()
    channels = ins.initialize_topology()
    results = list(futures.map(ins, populations, channels, server_ip_addrs, server_users,
                               server_passwords))
    dct = {}
    logger.info("fuuu")
    for data in results:
        best_chromosome = data.pop(0)
        fitness_val = best_chromosome.fit
        vector = best_chromosome.chromosome
        dct[fitness_val] = vector
    logger.info("END RESULTTTTTT " + str(sorted(dct.items()).pop()))


def run_coarse_grained_ga_remote(population_size, chromosome_size,
                                 number_of_generations,
                                 neighbourhood_size, server_user, server_password, server_ip_addr,
                                 num_of_migrants, fitness):
    logger.info(str(server_ip_addr) + str(server_user) + str(server_password))
    ins = CoarseGrainedBase(population_size=population_size, chromosome_size=chromosome_size,
                            number_of_generations=number_of_generations,
                            neighbourhood_size=neighbourhood_size,
                            num_of_migrants=num_of_migrants, fitness=fitness)


def make_one_for_each(item, amount):
    to_return = []
    for x in range(0, amount):
        to_return.insert(x, item)
    return to_return
