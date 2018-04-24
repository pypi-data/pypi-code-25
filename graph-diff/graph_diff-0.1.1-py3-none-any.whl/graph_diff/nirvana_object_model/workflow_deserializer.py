from graph_diff.nirvana_object_model.workflow import Workflow
from graph_diff.nirvana_object_model.workflow.block import Block
from graph_diff.nirvana_object_model.workflow.operation import Operation


def deserialize(json):
    workflow = Workflow()

    blocks = {}
    all_inputs = {}
    all_outputs = {}

    for block_json in json['result']['configurationSnapshot']['flowchart']['blocks']:
        operation_id = block_json['type']['_id']
        block_id = block_json['_id']

        inputs = []
        for input in block_json['inputs']:
            input_name = input['name']
            all_inputs[input['_id']] = (input_name, block_id)
            inputs.append(input_name)

        outputs = []
        for output in block_json['outputs']:
            output_name = output['name']
            all_outputs[output['_id']] = (output_name, block_id)
            outputs.append(output_name)

        operation = Operation(operation_id, inputs, outputs)
        block = Block(operation)

        count = workflow.add_block(block)

        blocks[block_id] = (block, count)

    for block_json in json['result']['configurationSnapshot']['flowchart']['blocks']:
        for incoming in block_json['incoming']:
            source_id = incoming['source']['@value']
            if source_id not in all_outputs:
                continue
            (source_name, source_block_id) = all_outputs[source_id]
            (source_block, source_block_count) = blocks[source_block_id]

            target_id = incoming['target']['@value']
            (target_name, target_block_id) = all_inputs[target_id]
            (target_block, target_block_count) = blocks[target_block_id]

            workflow.add_connection_by_data(source_block, source_block_count, source_name,
                                            target_block, target_block_count, target_name)

    return workflow
