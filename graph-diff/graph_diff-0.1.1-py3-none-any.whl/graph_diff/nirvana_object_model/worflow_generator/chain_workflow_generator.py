import random

import numpy

from graph_diff.nirvana_object_model.workflow import Workflow
from .standard_workflow_generator import StandardWorkflowGenerator


class ChainWorkflowGenerator(StandardWorkflowGenerator):
    """Generator for chained workflows"""

    def __init__(self):
        super().__init__()
        self.chain_number = None

    def generate_workflow(self) -> Workflow:
        """
        Generates workflow by set a given set of blocks.
        If types not given they may be generated.

        chain_number is a number of the chains, distribution is geometric
        with settable expectation.
        Then chain_number chains are created consisting of given types
        and connected by execution.
        After that chain_number random connections are generated.

        :return: generated workflow
        """

        if self.types_of_block is None:
            raise Exception("Blocks not set yet! Set them explicitly or generate them by generate_blocks method.")

        workflow = Workflow()
        chain_number = numpy.random.geometric(p=1 / self.chain_number) + 1

        for _ in range(0, chain_number):
            prev_block = self.types_of_block[0]
            prev_number = workflow.add_block(prev_block)

            for new_block in self.types_of_block[1:]:
                new_number = workflow.add_block(new_block)
                workflow.add_connection_by_execution(prev_block, prev_number, new_block, new_number)

                prev_block = new_block
                prev_number = new_number

        for _ in range(0, chain_number):
            from_block_num = random.randint(0, len(self.types_of_block) - 1)
            from_num = random.randint(0, chain_number - 1)

            to_block_num = random.randint(0, len(self.types_of_block) - 1)
            to_num = random.randint(0, chain_number - 1)

            if (from_block_num > to_block_num):
                from_block_num, to_block_num = to_block_num, from_block_num
                from_num, to_num = to_num, from_num

            from_block = self.types_of_block[from_block_num]
            to_block = self.types_of_block[to_block_num]

            workflow.add_connection_by_execution(from_block, from_num, to_block, to_num)

        return workflow

    def generate_blocks(self,
                        min_block_num=8,
                        max_block_num=12,
                        chain_number=20,
                        min_input_output_number=0,
                        max_input_output_number=3,
                        min_key_value_number=0,
                        max_key_value_number=10):
        """
        Generate blocks with given parameters.

        :param min_block_num:
        :param max_block_num:
        :param chain_number:
        :param min_input_output_number:
        :param max_input_output_number:
        :param min_key_value_number:
        :param max_key_value_number:
        :return:
        """
        super().generate_blocks(min_block_num,
                                max_block_num,
                                min_input_output_number,
                                max_input_output_number,
                                min_key_value_number,
                                max_key_value_number)
        self.chain_number = chain_number
        return self
