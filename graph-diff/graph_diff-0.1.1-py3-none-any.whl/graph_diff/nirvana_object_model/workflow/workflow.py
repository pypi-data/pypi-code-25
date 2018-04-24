from collections import defaultdict

from .block import Block


class Workflow:
    """Box class for nirvana workflow representation"""

    def __init__(self):
        self._blocks = []
        self._connections_by_execution = defaultdict(set)
        self._connections_by_data = defaultdict(set)

    def __iter__(self):
        return iter(self._blocks)

    def items_by_exc(self):
        return self._connections_by_execution.items()

    def items(self):
        return self._connections_by_data.items()

    def add_block(self, new_block: Block):
        self._blocks.append(new_block)
        return self._blocks.count(new_block)

    def add_connection_by_execution(self,
                                    from_block: Block,
                                    from_number: int,
                                    to_block: Block,
                                    to_number: int):
        assert from_block in self._blocks
        assert to_block in self._blocks
        assert from_number <= self._blocks.count(from_block)
        assert to_number <= self._blocks.count(to_block)

        self._connections_by_execution[from_block, from_number].add((to_block, to_number))
        return self

    def add_connection_by_data(self,
                               from_block: Block,
                               from_number: int,
                               output_nest: str,
                               to_block: Block,
                               to_number: int,
                               input_nest: str):
        assert from_block in self._blocks
        assert to_block in self._blocks
        assert from_number <= self._blocks.count(from_block)
        assert to_number <= self._blocks.count(to_block)
        assert output_nest in from_block.operation.outputs
        assert input_nest in to_block.operation.inputs

        self._connections_by_data[from_block, from_number, output_nest].add((to_block, to_number, input_nest))
        return self
