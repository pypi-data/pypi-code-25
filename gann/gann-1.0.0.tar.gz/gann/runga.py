import numpy as np
import time
import crossover
import mutation
import selection
import makegene


def evolve(n_task, fitness_precision, param,
           selection_way='sorting_selection', elitism=1,
           crossover_way='one_point_crossover', pc=0.6,
           mutation_way='simple_mutation', perturb=None, pm=0.1, pw=0.8, is_replace=True):
    DNA_length = len(param[0].w) + len(param[0].b)
    # select individual
    if selection_way == 'sorting_selection':
        new_cnn_id = selection.sorting_selection(list(range(0, n_task)), fitness_precision, n_task-elitism)
    # save the best individual into offspring
    best_id = np.argmax(fitness_precision)
    best_gene = makegene.make_gene(param[best_id])
    # encode parameters to gene
    genetic_populations = []
    for j in range(n_task - elitism):
        genetic_populations.append(makegene.make_gene(param[new_cnn_id[j]]))
    if crossover_way == 'one_point_crossover':
        genetic_populations = crossover.one_point_crossover(genetic_populations, pc, n_task-elitism)
    if mutation_way == 'simple_mutation':
        genetic_populations = mutation.simple_mutation(genetic_populations, n_task-elitism, DNA_length, perturb, pm, pw, is_replace)
    # save the best parent individual of gene
    for _ in range(elitism):
        genetic_populations.append(best_gene)

    # update offspring params into 'param' object list
    for j in range(n_task):
        # update weights and bias
        for k in range(int(DNA_length / 2)):
            param[j].w[k] = genetic_populations[j][2 * k]
            param[j].b[k] = genetic_populations[j][2 * k + 1]

    return param


def run_ga_nn(n_task, max_steps, cnn, generate_data, param, ga_step_decay,
              is_grad_des=True, test_cnn=None, is_equal_test=True,
              selection_way='sorting_selection', elitism=1,
              crossover_way='one_point_crossover', pc=0.6,
              mutation_way='simple_mutation', perturb=None, pm=0.1, pw=0.8, is_replace=True):
    if is_equal_test is True:
        test_cnn = cnn
    winner = 0.0
    winner_all = []  # winner of every step
    mean_f = []  # mean fitness of every step
    final_image, final_labels = generate_data.get_overall_test_data()
    start = time.time()
    for step in range(max_steps):
        fitness_precision = []
        ga_step = ga_step_decay(step)
        pr = np.zeros((ga_step, n_task))
        for i in range(n_task):
            if is_grad_des is True:
                # read weights and bias
                cnn.run_update_w(param[i].w)
                cnn.run_update_b(param[i].b)
                for _ in range(ga_step):
                    if i != n_task - elitism:
                        x_batch, y_batch = generate_data.get_batch_train_data()
                        cnn.run_train_op(x_batch, y_batch)
                    param[i].w = list(cnn.get_all_w())
                    param[i].b = list(cnn.get_all_b())

                    test_cnn.run_update_w(param[i].w)
                    test_cnn.run_update_b(param[i].b)
                    # get fitness about classification accuracy
                    pr[_, i] = test_cnn.get_fitness(final_image, final_labels)
                # save parameters into param object
                param[i].w = list(cnn.get_all_w())
                param[i].b = list(cnn.get_all_b())
            test_cnn.run_update_w(param[i].w)
            test_cnn.run_update_b(param[i].b)
            # 利用测试数据测试准确率
            fitness_precision.append(test_cnn.get_fitness(final_image, final_labels))
        if is_grad_des is True:
            wr = np.max(pr, axis=1)
            mr = np.mean(pr, axis=1)
            for x in range(ga_step):
                winner = max(winner, wr[x])
                winner_all.append(winner)
                mean_f.append(mr[x])
        else:
            winner = max(winner, np.max(fitness_precision))

        print('step: %d ' % step,
              'precision: ', np.array(fitness_precision).copy().astype(np.float16),
              'winner: %.3f' % winner,
              'duration: %.3f' % (time.time()-start))
        start = time.time()
        '''
        if step != max_steps - 1:
            param = evolve(n_task, fitness_precision, param,
                           selection_way, elitism,
                           crossover_way, pc,
                           mutation_way, perturb, pm, pw, is_replace)
        '''

    np.save('data/winner.npy', np.array(winner_all))
    np.save('data/mean.npy', np.array(mean_f))
    print('winner: %.3f' % winner)

    return param
