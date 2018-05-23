from tec.ic.ia.pc2.g07.algorithms.Algorithm import Algorithm
from queue import Queue
import random
import itertools
import os

"""
This class implements an A* algorithm to solve a path-finding problem.
"""


class A_Star(Algorithm):
    def __init__(self, board, vision, carrots, MaxLastMovements):
        super().__init__(board)
        self.vision = vision
        self.carrots = carrots
        #A* Variables
        self.open = []  # List to store possible states
        self.f = []  # List to store cost function for every possible state
        self.g = 0  # Acumulated cost
        self.LastMovements = []  # List to store the N last movements
        # Specify the N value on self.LastMovements
        self.MaxLastMovements = MaxLastMovements
        self.totalCost = 0  # Stores the total cost of every decision made.

    # Function for establish a seed on random generator
    def set_random_seed(self, seed):
        random.seed(seed)

    # Function for search where is located the rabbit at start
    def search_start(self, board):
        for row in range(len(board)):
            if 'C' in board[row]:
                return [row, board[row].index('C')]
        print("\nThe file does not contain a rabbit.")
        exit(-1)

    # Function to check a coordinate is aceptable (in-borders of the board)
    def is_in_board(self, x, y, board):
        try:
            if x < 0 or y < 0:
                return False
            dummy = board[x][y]
            return True
        except:
            return False

    # Function to search all possible neighbors states that are in-borders
    def search_neighbors(self, current_state, board):
        neighbors = [[0, -1], [0, 1], [-1, 0], [1, 0]]
        succesors = []
        for neighbor in neighbors:
            x = current_state[0] + neighbor[0]
            y = current_state[1] + neighbor[1]
            if self.is_in_board(x, y, board):
                succesors.append([x, y])
        return succesors

    # Function to get the state with lowest cost, tie is solved by randomness
    def get_lower(self):
        best = min(self.f)
        count = self.f.count(best)
        if count == 1:
            return best, self.open[self.f.index(best)]
        else:
            indixes = [i for i, x in enumerate(self.f) if x == best]
            return best, self.open[random.choice(indixes)]

    # Function to store the last movement
    def put_Last_Movement(self, state):
        if len(self.LastMovements) == self.MaxLastMovements:
            self.LastMovements = self.LastMovements[1:]
        self.LastMovements.append(state)

    # Function to print the solution on screen
    def pretty_print(self, last, current):
        movements_indexes = [[0, -1], [0, 1], [-1, 0], [1, 0]]
        movements = ["LEFT", "RIGHT", "UP", "DOWN"]
        index = [current[0]-last[0], current[1]-last[1]]
        i = movements_indexes.index(index)
        movement = movements[i]

        step = "Step: %05d" % (self.g,)
        for direction_index in range(len(movements)):
            mov_index = movements_indexes[direction_index]
            index = [last[0]+mov_index[0], last[1]+mov_index[1]]
            cost = "Out of Borders"
            if index in self.open:
                cost = self.f[self.open.index(index)]
            step += " "+movements[direction_index]+": "+str(cost)
        move = " Movement: "+movement
        print(step + move)

    # Function to get the carrots' coordinates that are in the vision field
    def carrots_in_sight(self, current_state, board):
        posibilites = list(range(-self.vision, self.vision+1))
        vision_field_indexes = [[x, y]
                                for x in posibilites for y in posibilites]
        vision_field_indexes.remove([0, 0])
        carrots_coordinates = []
        for field in vision_field_indexes:
            x = current_state[0] + field[0]
            y = current_state[1] + field[1]
            if self.is_in_board(x, y, board) and board[x][y] == 'Z':
                carrots_coordinates.append([x, y])
        return carrots_coordinates

    # Function to calculate the heuristic without considering the carrots
    def h_without_carrots(self):
        h = []
        for possible_state in self.open:
            # Last immediate direction
            if possible_state in self.LastMovements[-1:]:
                h.append(10)
            # Being there lately
            elif possible_state in self.LastMovements[:-1]:
                h.append(5)
            # Not being there
            else:
                h.append(1)
        return h

    # Function that calculates how many carrots can reach (at future) from one movement
    def carrots_at_reach_from_movement(self, carrots_coordinates, possible_state, relevant_index, operation):
        carrots_at_reach = 0
        for carrot in carrots_coordinates:
            if operation == "<=":
                if carrot[relevant_index] <= possible_state[relevant_index]:
                    carrots_at_reach += 1
            elif operation == ">=":
                if carrot[relevant_index] >= possible_state[relevant_index]:
                    carrots_at_reach += 1
        return carrots_at_reach

    # Function to calculate heuristic conseidering the carrots in vision field
    def h_with_carrots(self, carrots_coordinates, current):
        h = []
        for possible_state in self.open:
            nearest_carrot_distance = abs(
                possible_state[0]-carrots_coordinates[0][0]) + abs(possible_state[1]-carrots_coordinates[0][1])
            for carrot in carrots_coordinates[1:]:
                distance = abs(
                    possible_state[0]-carrot[0]) + abs(possible_state[1]-carrot[1])
                if distance < nearest_carrot_distance:
                    nearest_carrot_distance = distance

            index = [possible_state[0]-current[0], possible_state[1]-current[1]]
            carrots_at_reach = 0
            if index == [0, -1]:  # Left
                carrots_at_reach = self.carrots_at_reach_from_movement(
                    carrots_coordinates, possible_state, relevant_index=1, operation="<=")
            elif index == [0, 1]:  # Right
                carrots_at_reach = self.carrots_at_reach_from_movement(
                    carrots_coordinates, possible_state, relevant_index=1, operation=">=")
            elif index == [-1, 0]:  # Up
                carrots_at_reach = self.carrots_at_reach_from_movement(
                    carrots_coordinates, possible_state, relevant_index=0, operation="<=")
            elif index == [1, 0]:  # Down
                carrots_at_reach = self.carrots_at_reach_from_movement(
                    carrots_coordinates, possible_state, relevant_index=0, operation=">=")

            h.append(nearest_carrot_distance +
                     len(carrots_coordinates) - carrots_at_reach)
        return h

    # Function to calculate the cost function for every possible state
    def calculate_f_score(self, current_state, board):
        g = [self.g for i in self.open]
        carrots_coordinates = self.carrots_in_sight(current_state, board)
        h_without_carrots = self.h_without_carrots()
        if carrots_coordinates != []:
            h_with_carrots = self.h_with_carrots(carrots_coordinates, current_state)
        else:
            h_with_carrots = [0 for i in self.open]

        self.f = [x + y + z for x, y, z in zip(g, h_without_carrots, h_with_carrots)]

    # Function to save the board in a file, file name is the step of execution
    def save_board_A_star(self, index):
        basedir = os.path.dirname(
            "Results_A_star\\00001.txt")
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        with open("Results_A_star\\%05d.txt" % (index,), "w+") as file:
            for row in self.board:
                file.writelines(row)
                file.write("\n")

    # Function to execute A* algorithm
    def execute(self):
        self.remove_last_results("Results_A_star")
        self.open.append(self.search_start(self.board))
        self.f.append(0)
        carrots_found = 0

        cost, current = self.get_lower()

        while len(self.open) != 0:
            if carrots_found == self.carrots:
                print("Step: %05d FINAL ; Total Costo: %d" %
                      (self.g, self.totalCost,))
                break

            # Refresh neighbors
            self.open = self.search_neighbors(current, self.board)

            # f(state) = g(state) + h(state)
            self.calculate_f_score(current, self.board)

            # Stores last movement
            self.put_Last_Movement(current)
            last = current
            self.totalCost += cost

            # Move
            cost, current = self.get_lower()
            self.g += 1
            self.pretty_print(last, current)

            # If found a carrot
            if self.board[current[0]][current[1]] == 'Z':
                carrots_found += 1

            # Refresh board
            self.board[last[0]][last[1]] = " "
            self.board[current[0]][current[1]] = "C"

            self.save_board_A_star(self.g)
