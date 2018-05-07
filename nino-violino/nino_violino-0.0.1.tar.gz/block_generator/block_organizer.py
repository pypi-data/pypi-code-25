import random, copy

def get_ending_of_block(timing_data):
    block_end = timing_data['starting_beats'][-1] + timing_data['number_of_bars'] * timing_data['bar_length']
    return block_end


def shuffle_blocks(blocks):
    shuffled_blocks = []
    while any([b['block_data']['block_occurences'] for b in blocks]):
        new_block = random.choice(blocks)

        if len(shuffled_blocks) > 1 and len(blocks) > 1:
            if new_block['block_data']['id'] == shuffled_blocks[-1] == shuffled_blocks[-2]:
                continue
        if new_block['block_data']['block_occurences'] == 0: 
            continue

        shuffled_blocks.append(copy.deepcopy(new_block))
        new_block['block_data']['block_occurences'] -= 1
    return shuffled_blocks

def get_shuffled_blocks(blocks):
    new_blocks = copy.deepcopy(blocks)
    shuffled_blocks = shuffle_blocks(new_blocks)

    for b in range(1, len(shuffled_blocks)): 
        block_t_data = shuffled_blocks[b]['structure_data']['timing_data']
        last_block_t_data = shuffled_blocks[b-1]['structure_data']['timing_data']
        new_starting_beats = [get_ending_of_block(last_block_t_data) + starting_beat for starting_beat in block_t_data['starting_beats']]

        shuffled_blocks[b]['structure_data']['timing_data']['starting_beats'] = new_starting_beats

    return shuffled_blocks


#This is kind of a hacky solution, so I should probably think of a better way to do it. 
#Basically, I copy each block based on its number of occurences (block['block_data']['block_occurences']), which makes it easier to calculate the starting beats. 
#Then I find all corresponding original blocks based on the block_id, and add up the starting beats. 
def organize_blocks(blocks):
    shuffled_blocks = get_shuffled_blocks(blocks)
    for block in blocks: 
        block['structure_data']['timing_data']['starting_beats'] = []

    for block in blocks: 
        for s_block in shuffled_blocks: 
            if block['block_data']['id'] == s_block['block_data']['id']: 
                block['structure_data']['timing_data']['starting_beats'] += s_block['structure_data']['timing_data']['starting_beats']

    return blocks
