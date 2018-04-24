from graph_diff.new_ant_algorithm import parameters


class PheromonTable:
    """Lazy pheromon table for the ant algorithm"""

    P = parameters.P

    def __init__(self):
        self.table = {}
        self.last_update = {}
        self.current_iteration = 0

    # O(1)
    def get_element(self, u, u1, v, v1):
        if (u, u1, v, v1) not in self.table.keys():
            return (1 - PheromonTable.P) ** self.current_iteration
        else:
            return self.table[u, u1, v, v1] * (1 - PheromonTable.P) \
                   ** (self.current_iteration - self.last_update[u, u1, v, v1])

    # O(1)
    def add_update(self, u, u1, v, v1, value):
        if (u, u1, v, v1) not in self.table.keys():
            self.table[u, u1, v, v1] = 1
            self.last_update[u, u1, v, v1] = 0
        self.table[u, u1, v, v1] *= (1 - PheromonTable.P) ** (self.current_iteration - self.last_update[u, u1, v, v1])
        self.table[u, u1, v, v1] += value
        self.last_update[u, u1, v, v1] = self.current_iteration

    # O(1)
    def next_iteration(self):
        self.current_iteration += 1
