import copy, sys, os
from block_parser import block_parser

testing_dir = os.getcwd()

block_template = {
    "block_data" : {
        "id" : "",
        "blocks" : [],
    },
    "structure_data" : {
        "notes_data" : {
        },
        "timing_data" : {
        },
    }
}

def get_next_block():
    i = 0
    block_len = 4
    while True: 
        block_start = i*block_len
        block_end = block_start + block_len

        block = {
            'block_data' : {
                'id' : i, 
                'program_number' : i,
                'track' : 1 
            },
            'structure_data' : {
                'notes_data' : {
                    'chord_progression' : [
                        {
                        'chord_type' : 'major', 
                        'chord_root' : 'A3',
                        }
                    ]
                },
                'timing_data' : {
                    'starting_beats' : [block_start], 
                    'number_of_bars' : 1, 
                    'bar_length' : block_len
                }
            }
        }
        print 'Block from %s : %s has program %s. ' % (block_start, block_end, i)
        i += 1

        yield block


def generate_song():

    if len(sys.argv) < 2: 
        print 'Usage: python soundfont_tester.py <soundfont> [number_of_instruments]'
        sys.exit()

    if len(sys.argv) == 3: 
        number_of_blocks = int(sys.argv[2])
    else: 
        number_of_blocks = 80

    soundfont = sys.argv[1]

    base_block = copy.deepcopy(block_template)
    base_block['block_data']['bpm'] = 120
    base_block['structure_data']['notes_data']['base_volume'] = 120

    block_gen = get_next_block()
    for block in range(number_of_blocks):
        new_block = next(block_gen)
        base_block['block_data']['blocks'].append(new_block)

    song_path = '%s/%s_test' % (testing_dir, soundfont)
    block_parser.make_block_music(base_block, soundfont = soundfont, song_name = song_path)

    return base_block


generate_song()
