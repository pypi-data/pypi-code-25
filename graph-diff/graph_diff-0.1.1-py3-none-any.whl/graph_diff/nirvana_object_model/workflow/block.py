from .operation import Operation


class Block:
    """Class representing nirvana block"""

    def __init__(self, operation: Operation, options=None):
        """
        Contains operation and options that are key-value

        :param operation:   nirvana operation
        :param options:     dict of options
        """

        if options is None:
            options = {}
        self.operation = operation
        self.options = tuple(sorted(options.items())) if type(options) is dict else tuple(sorted(options))

    def __hash__(self):
        return hash(self.operation) ^ hash(self.options)

    def __eq__(self, other):
        return self.options == other.options and self.operation == other.operation
