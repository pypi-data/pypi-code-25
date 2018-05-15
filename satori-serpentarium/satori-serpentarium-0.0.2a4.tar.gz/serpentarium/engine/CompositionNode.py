import uuid


class CompositionNode:
    """
    CompositionNode is a representation of Mod metadata parsed from a configuration.
    Is used as a vertex in an execution graph.
    Must be hashable.
    """

    def __init__(self, name: str, id: uuid, connectors=None) -> None:
        """

        :param name: Unique node name
        :param id: Unique id
        :param connectors: neighbour node names
        """
        if connectors is None:
            connectors = []
        self.name = name
        self.connectors = connectors
        self.id = id

    def __hash__(self) -> int:
        return self.name.__hash__()

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def __str__(self) -> str:
        return self.name
