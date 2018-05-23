from tec.ic.ia.pc2.g07.algorithms.Genetic import Genetic
from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.Individual import Individual
from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.Random_CrossOver import Random_CrossOver
from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.Sons_of_Sons_CrossOver import Sons_of_Sons_CrossOver

'''
[GA] Generate the 2 first individuals, every each with the same content as the original board.
Function tested: first_birth()
Outputs: A list containing every individual.
'''
def test_generate_2_first_individuals():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    gene_as_board = [' ', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' ']
    ga = Genetic(board, direction="izquierda", number_individuals=2, number_generations=1, crossover=None, mutation_rate=5)
    new_individuals = ga.first_birth(template=board, amount=2)
    assert len(new_individuals) == 2
    assert new_individuals[0].gene==gene_as_board and new_individuals[1].gene==gene_as_board

'''
[GA] Mutate individual with mutation rate = 0.
Function tested: mutate_population()
Outputs: The population without changes.
'''
def test_mutate_population_with_mutation_rate_0():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    gene_as_board = [' ', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' ']
    ga = Genetic(board, direction="izquierda", number_individuals=2, number_generations=1, crossover=None, mutation_rate=5)
    population = ga.first_birth(template=board, amount=2)
    ga.mutate_population(population, mutation_rate=0)
    assert len(population) == 2
    assert population[0].gene==gene_as_board and population[1].gene==gene_as_board

'''
[GA] Mutate individual with mutation rate = 50.
Function tested: mutate_population()
Outputs: The population with one extra individual.
'''
def test_mutate_population_with_mutation_rate_50():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    gene_as_board = [' ', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' ']
    ga = Genetic(board, direction="izquierda", number_individuals=2, number_generations=1, crossover=None, mutation_rate=50)
    ga.set_random_seed(3)
    population = ga.first_birth(template=board, amount=2)
    ga.mutate_population(population, mutation_rate=50)
    assert len(population) == 3
    assert population[0].gene==gene_as_board and population[1].gene==gene_as_board and population[2].gene!=gene_as_board

'''
[GA] Mutate individual with mutation rate = 100.
    Only three individuals because one was trying to change a field with a carrot.
Function tested: mutate_population()
Outputs: The population with one extra individuals.
'''
def test_mutate_population_with_mutation_rate_100_but_one_individual_is_discarted():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    gene_as_board = [' ', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' ']
    ga = Genetic(board, direction="izquierda", number_individuals=2, number_generations=1, crossover=None, mutation_rate=100)
    ga.set_random_seed(3)
    population = ga.first_birth(template=board, amount=2)
    ga.mutate_population(population, mutation_rate=100)
    assert len(population) == 3
    assert population[0].gene==gene_as_board and population[1].gene==gene_as_board and population[2].gene!=gene_as_board

'''
[GA] Checks if a field [1,1] is in a board of 3x3.
Function tested: is_in_board()
Outputs: True.
'''
def test_1_1_is_in_board_3x3():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    ga = Genetic(board, direction="izquierda", number_individuals=2, number_generations=1, crossover=None, mutation_rate=100)
    ga.rows_in_board = 3
    ga.cols_in_board = 3
    assert ga.is_in_board(x=1,y=1) == True

'''
[GA] Checks if a field [4,5] is in a board of 3x3.
Function tested: is_in_board()
Outputs: False.
'''
def test_4_5_is_in_board_3x3():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    ga = Genetic(board, direction="izquierda", number_individuals=2, number_generations=1, crossover=None, mutation_rate=100)
    ga.rows_in_board = 3
    ga.cols_in_board = 3
    assert ga.is_in_board(x=4,y=5) == False

'''
[GA] Checks if a field [-1,2] is in a board of 3x3.
Function tested: is_in_board()
Outputs: False.
'''
def test_minus1_2_is_in_board_3x3():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    ga = Genetic(board, direction="izquierda", number_individuals=2, number_generations=1, crossover=None, mutation_rate=100)
    ga.rows_in_board = 3
    ga.cols_in_board = 3
    assert ga.is_in_board(x=-1,y=2) == False


'''
[GA] Calculates fitness with left direction. The individual is the best possibly created.
Function tested: calculate_fitness()
Outputs: The individual with its fitness changed.
'''
def test_fitness_with_best_individual():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    ga = Genetic(board, direction="izquierda", number_individuals=2, number_generations=1, crossover=None, mutation_rate=100)
    individual_tested = Individual(gene=['V', ' ', 'C', 'Z', ' ', ' ', '>', 'Z', ' '])
    ga.rows_in_board = 3
    ga.cols_in_board = 3
    ga.calculate_fitness([individual_tested])
    assert individual_tested.fitness == 236

'''
[GA] Calculates fitness with left direction. The individual is not optimal solution.
Function tested: calculate_fitness()
Outputs: The individual with its fitness changed.
'''
def test_fitness_with_bad_individual():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    ga = Genetic(board, direction="izquierda", number_individuals=2, number_generations=1, crossover=None, mutation_rate=100)
    individual_tested = Individual(gene=[' ', 'V', 'C', 'Z', '<', ' ', ' ', 'Z', '<'])
    ga.rows_in_board = 3
    ga.cols_in_board = 3
    ga.calculate_fitness([individual_tested])
    assert individual_tested.fitness == -32

'''
[GA] Calculates fitness with down direction. The individual is near to the best possibly created.
Function tested: calculate_fitness()
Outputs: The individual with its fitness changed.
'''
def test_fitness_with_almost_best_individual():
    board = [[" "," ","C"],["Z"," "," "],[" ","Z"," "]]
    ga = Genetic(board, direction="abajo", number_individuals=2, number_generations=1, crossover=None, mutation_rate=100)
    individual_tested = Individual(gene=['>', ' ', 'C', 'Z', ' ', ' ', 'A', 'Z', '<'])
    ga.rows_in_board = 3
    ga.cols_in_board = 3
    ga.calculate_fitness([individual_tested])
    assert individual_tested.fitness == 196

'''
[GA - CrossOver] Gets the son of 2 selected parents at random crossover.
Function tested: cross() at Random_CrossOver
Outputs: The new individual.
'''
def test_2_parents_random_crossover():
    crossover = Random_CrossOver(parents_amount=2)
    first_parent = Individual(gene=['>', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' '])
    second_parent = Individual(gene=[' ', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', '<'])
    new_individual = crossover.cross(parents=[first_parent, second_parent])
    assert new_individual.gene == ['>', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', '<']

'''
[GA - CrossOver] Gets the son of 3 selected parents at random crossover.
Function tested: cross() at Random_CrossOver
Outputs: The new individual.
'''
def test_3_parents_random_crossover():
    crossover = Random_CrossOver(parents_amount=3)
    first_parent = Individual(gene=['>', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' '])
    second_parent = Individual(gene=[' ', ' ', 'C', 'Z', 'A', ' ', ' ', 'Z', ' '])
    third_parent = Individual(gene=[' ', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', '<'])
    new_individual = crossover.cross(parents=[first_parent, second_parent, third_parent])
    assert new_individual.gene == ['>', ' ', 'C', 'Z', 'A', ' ', ' ', 'Z', '<']

'''
[GA - CrossOver] Gets the son of 2 selected parents at sons of sons crossover.
Function tested: cross() at Sons_of_Sons_CrossOver
Outputs: The new individual.
'''
def test_2_parents_sons_of_sons_crossover():
    crossover = Sons_of_Sons_CrossOver(parents_amount=2)
    crossover.set_random_seed(11)
    first_parent = Individual(gene=['>', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' '])
    second_parent = Individual(gene=[' ', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', '<'])
    new_individual = crossover.cross(parents=[first_parent, second_parent])
    assert new_individual.gene == ['>', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', '<']


'''
[GA - CrossOver] Gets the son of 3 selected parents at sons of sons crossover.
Function tested: cross() at Sons_of_Sons_CrossOver
Outputs: The new individual.
'''
def test_3_parents_sons_of_sons_crossover():
    crossover = Sons_of_Sons_CrossOver(parents_amount=3)
    crossover.set_random_seed(2)
    first_parent = Individual(gene=['V', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' '])
    second_parent = Individual(gene=['>', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' '])
    third_parent = Individual(gene=[' ', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', '<'])
    new_individual = crossover.cross(parents=[first_parent, second_parent, third_parent])
    assert new_individual.gene == ['>', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' ']

'''
[GA - CrossOver] Gets the son of 4 selected parents at sons of sons crossover.
Function tested: cross() at Sons_of_Sons_CrossOver
Outputs: The new individual.
'''
def test_4_parents_sons_of_sons_crossover():
    crossover = Sons_of_Sons_CrossOver(parents_amount=4)
    crossover.set_random_seed(2)
    first_parent = Individual(gene=['V', ' ', 'C', 'Z', ' ', ' ', ' ', 'Z', ' '])
    second_parent = Individual(gene=[' ', ' ', 'C', 'Z', ' ', ' ', '>', 'Z', ' '])
    third_parent = Individual(gene=[' ', '<', 'C', 'Z', ' ', ' ', ' ', 'Z', '<'])
    fourth_parent = Individual(gene=[' ', ' ', 'C', 'Z', ' ', ' ', '<', 'Z', ' '])
    new_individual = crossover.cross(parents=[first_parent, second_parent, third_parent, fourth_parent])
    assert new_individual.gene == [' ', '<', 'C', 'Z', ' ', ' ', '>', 'Z', ' ']
