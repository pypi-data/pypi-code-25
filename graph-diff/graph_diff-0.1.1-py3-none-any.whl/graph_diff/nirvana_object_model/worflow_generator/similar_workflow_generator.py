import random
from collections import defaultdict

from graph_diff.nirvana_object_model.workflow import Workflow
from .standard_workflow_generator import StandardWorkflowGenerator
from .workflow_generator import WorkflowGenerator


class SimilarWorkflowGenerator(WorkflowGenerator):
    """Class that generates workflow and then slightly changes it"""

    def __init__(self,
                 change_probability=0.2,
                 min_block_num=10,
                 max_block_num=20,
                 min_input_output_number=0,
                 max_input_output_number=3,
                 min_key_value_number=0,
                 max_key_value_number=10):
        """
        :param change_probability:      probability of element deletion/addition
        :param min_block_num:
        :param max_block_num:
        :param min_input_output_number:
        :param max_input_output_number:
        :param min_key_value_number:
        :param max_key_value_number:
        """
        self.standard_workflow = StandardWorkflowGenerator() \
            .generate_blocks(min_block_num,
                             max_block_num,
                             min_input_output_number,
                             max_input_output_number,
                             min_key_value_number,
                             max_key_value_number).generate_workflow()
        self.change_probability = change_probability

    def generate_workflow(self) -> Workflow:
        """
        Changes standard generated workflow slightly and returns new version.

        :return:    generated workflow
        """

        workflow = Workflow()

        num = {}
        original_nums = defaultdict(int)
        for block in self.standard_workflow:
            original_nums[block] += 1
            p = random.uniform(0, 1)
            if p >= self.change_probability:
                num[block, original_nums[block]] = workflow.add_block(block)

        for (from_block, from_num, output_nest), to_set in self.standard_workflow.items():
            for to_block, to_num, input_nest in to_set:
                try:
                    p = random.uniform(0, 1)
                    if p >= self.change_probability:
                        workflow.add_connection_by_data(from_block,
                                                        from_num,
                                                        output_nest,
                                                        to_block,
                                                        to_num,
                                                        input_nest)
                except AssertionError:
                    pass
        for (from_block, from_num), to_set in self.standard_workflow.items_by_exc():
            for to_block, to_num in to_set:
                try:
                    p = random.uniform(0, 1)
                    if p >= self.change_probability:
                        workflow.add_connection_by_execution(from_block,
                                                             from_num,
                                                             to_block,
                                                             to_num)
                except AssertionError:
                    pass

        return workflow
