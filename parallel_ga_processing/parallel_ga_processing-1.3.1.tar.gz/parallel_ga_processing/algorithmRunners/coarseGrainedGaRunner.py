import uuid
from scoop import futures, logger
from parallel_ga_processing.geneticAlgorithms import CoarseGrainedBase
from parallel_ga_processing.geneticAlgorithms import Messenger
from parallel_ga_processing.geneticAlgorithms import ProductionQueue


def run_coarse_grained_ga(population_size, chromosome_size,
                          number_of_generations,
                          neighbourhood_size, server_user, server_password, server_ip_addr,
                          num_of_migrants, fitness):
    ins = CoarseGrainedBase(population_size=population_size, chromosome_size=chromosome_size,
                            number_of_generations=number_of_generations,
                            neighbourhood_size=neighbourhood_size,
                            num_of_migrants=num_of_migrants, fitness=fitness)

    x, y = population_size
    populations = ins.initialize_population()
    channels = ins.initialize_topology()
    messengers = make_one_for_each(server_user, server_password, server_ip_addr, channels, x*y)

    results = list(futures.map(ins, populations, messengers))
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


def make_one_for_each(server_user, server_password, server_ip_addr, channels, amount):
    queue_to_produce = int(channels.pop(0))
    queues_to_consume = list(map(int, channels.pop(0)))
    to_return = list()
    for x in range(0, amount):
        to_return.append(Messenger(server_user=server_user, server_password=server_password,
                                   server_ip_addr=server_ip_addr,
                                   exchange='direct_logs', exchange_type='direct',
                                   subscription_routing_keys=queues_to_consume,
                                   production_routing_keys=queue_to_produce,
                                   queue=str(uuid.uuid4()),
                                   produced_messages=ProductionQueue(),
                                   consumed_messages=ProductionQueue()))
    return to_return
