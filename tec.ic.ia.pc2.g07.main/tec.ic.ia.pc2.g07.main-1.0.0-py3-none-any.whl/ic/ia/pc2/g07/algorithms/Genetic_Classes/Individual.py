
"""
This class implements a genetic algorithm individual.
"""


class Individual():
    def __init__(self, gene):
        self.gene = gene
        self.fitness = 0
        self.board = []

    def get_part(self, part_number, number_of_breaks):
        average = len(self.gene) / float(number_of_breaks)
        result = []
        last = 0.0

        while last < len(self.gene):
            result.append(self.gene[int(last):int(last + average)])
            last += average
        return result[part_number]

    def amount_of_signals(self):
        return len(self.gene) - (self.gene.count(" ") + self.gene.count("C") + self.gene.count("Z"))

    def gene_as_board(self, cols):
        board = []
        row = []
        cont = 0
        for i in self.gene:
            if cont == cols:
                board.append(row)
                row=[]
                cont=0
            row.append(i)
            cont+=1
        board.append(row)
        self.board = board
        return board


    # def __lt__(self, other):
    #     return self.fitness < other.fitness
    #
    # def __repr__(self):
    #     return str([self.gene, self.fitness])
    #
    # def __str__(self):
    #     return str([self.gene, self.fitness])
