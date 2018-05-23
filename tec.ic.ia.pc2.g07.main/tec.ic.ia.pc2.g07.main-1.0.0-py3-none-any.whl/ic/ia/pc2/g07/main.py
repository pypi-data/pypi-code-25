import argparse

from tec.ic.ia.pc2.g07.algorithms.A_Star import A_Star
from tec.ic.ia.pc2.g07.algorithms.Genetic import Genetic
from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.Random_CrossOver import Random_CrossOver
from tec.ic.ia.pc2.g07.algorithms.Genetic_Classes.Sons_of_Sons_CrossOver import Sons_of_Sons_CrossOver

parser = argparse.ArgumentParser(
    description='This program allows to execute a path-finding algortihm. It can be A* or a genetic algorithm for scenario changes.')

# A*
parser.add_argument("--a-estrella",
                    action="store_true", help="A* Algorithm.")
parser.add_argument("--vision", type=int, help="Vision field range.")
parser.add_argument("--zanahorias", type=int,
                    help="Objective's amount to search.")
parser.add_argument("--movimientos-pasados", type=int,
                    help="Number of past movements to store. (Default 5)")

# Genetic Algorithm
parser.add_argument("--genetico",
                    action="store_true", help="Genetic Algorithm.")
parser.add_argument("--derecha", action="store_true",
                    help="All individual going to the right.")
parser.add_argument("--izquierda", action="store_true",
                    help="All individual going to the left.")
parser.add_argument("--arriba", action="store_true",
                    help="All individual going up.")
parser.add_argument("--abajo", action="store_true",
                    help="All individual going down.")
parser.add_argument("--individuos", type=int, help="Individual's amount.")
parser.add_argument("--generaciones", type=int, help="Generation's amount.")
parser.add_argument("--politica-cruce",
                    choices=["random", "sons_of_sons"], help="Crossover algorithm.")
parser.add_argument("--cantidad-padres", type=int, help="Number of parents.")
parser.add_argument("--tasa-mutacion", type=int, help="Mutation Rate Percent.")

# Main Program
parser.add_argument("--tablero-inicial", required=True,
                    help="Input file destination. File containing the scenario to be resolved.")

args = parser.parse_args()

# Checks if just one algorithm is selected
cont_unique_flag = 0
unique_flags = ["a_estrella", "genetico"]
for flag in unique_flags:
    if args.__dict__[flag]:
        cont_unique_flag += 1

if cont_unique_flag != 1:
    parser.error("The application needs ONE algorithm per execution.")
    exit(-1)

algorithm = None
# Checks algorithm selected parameters
if args.a_estrella:
    if args.vision is None or args.zanahorias is None:
        parser.error(
            "The A* algorithm needs to know the vision field range and carrot's amount.")
        exit(-1)
    elif args.vision < 1 or args.zanahorias < 1:
        parser.error(
            "The A* algorithm needs to know the vision field range and carrot's amount. (>=1)")
        exit(-1)
    if args.movimientos_pasados is not None:
        movimientos_pasados = args.movimientos_pasados
    else:
        movimientos_pasados = 5

    algorithm = A_Star(board=None, vision=args.vision,
                       carrots=args.zanahorias, MaxLastMovements=movimientos_pasados)

elif args.genetico:
    # Checks if just one direction is selected
    cont_unique_flag = 0
    direction = ""
    unique_flags = ["derecha", "izquierda", "arriba", "abajo"]
    for flag in unique_flags:
        if args.__dict__[flag]:
            cont_unique_flag += 1
            direction = flag

    if cont_unique_flag != 1:
        parser.error("The genetic algorithm need just one direction.")
        exit(-1)
    if args.individuos is None or args.generaciones is None:
        parser.error(
            "The genetic algorithm needs to know the individual's and generation's amount.")
        exit(-1)
    elif args.individuos < 2 or args.generaciones < 1 or args.individuos > 99999 or args.generaciones > 99999:
        parser.error(
            "The genetic algorithm needs to know the individual's and generation's amount. (1-99999)")
        exit(-1)
    if args.politica_cruce is None or args.tasa_mutacion is None or args.cantidad_padres is None:
        parser.error(
            "The genetic algorithm needs to know the crossover algorithm, the number of parents and mutation rate.")
        exit(-1)
    elif args.tasa_mutacion < 0 or args.tasa_mutacion > 100:
        parser.error(
            "The genetic algorithm needs to know the mutation rate. (0-100)")
        exit(-1)
    elif args.cantidad_padres < 2 or args.cantidad_padres > args.individuos:
        parser.error(
            "The genetic algorithm needs to know the number of parents. (2-"+str(args.individuos)+")")
        exit(-1)

    if args.politica_cruce == "random":
        crossover = Random_CrossOver(args.cantidad_padres)
    elif args.politica_cruce == "sons_of_sons":
        crossover = Sons_of_Sons_CrossOver(args.cantidad_padres)

    algorithm = Genetic(board=None, direction=direction,
                        number_individuals=args.individuos, number_generations=args.generaciones,
                        crossover=crossover, mutation_rate=args.tasa_mutacion)

# Read the board
board = []
with open(args.tablero_inicial) as file:
    for rows in file.readlines():
        row = []
        for col in rows[:-1]:
            row.append(col)
        board.append(row)

# Validate the board (every row has the same amount of columns)
row_count = [len(row) for row in board]
if row_count.count(row_count[0]) != len(row_count) or board == []:
    parser.error(
        "The board needs to have the same size on every row. (>=1)")
    exit(-1)

# Validate the board (number of parents less than board size)
elif args.genetico and args.cantidad_padres > len(board)*len(board[0]):
    parser.error(
        "The genetic algorithm needs to know the number of parents. (2-"+str(len(board)*len(board[0]))+")")
    exit(-1)

# Execute the algorithm
algorithm.board = board
algorithm.execute()
