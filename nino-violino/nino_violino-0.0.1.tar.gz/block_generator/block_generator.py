import block_organizer, copy, uuid
from block_parser import block_parser, note_generator, chord_handler, instrument_handler

from violino_conf import configuration as gen_conf
from song_namer.names_generator import get_name
import random, copy, math


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

percussion_block = {
    'block_data' : {
        'track' : 9,
        'channel' : 9,
        'blocks' : [
            {'block_data' : {}, 'structure_data' : {'notes_data' : {}, 'timing_data' : {}}}, 
        ]
    },
    'structure_data' : {
        'notes_data' : {
            'chord_progression' :[
                { 
                    'chord_root' : 'C1',
                    'chord_type' : 'percussion',
                }
            ],
            'base_volume' : 100,
        },
        'timing_data' : {
        }
    }
}


block_template = gen_conf.get('block_template') or block_template


def get_block_bpm(block):
    if random.random() < gen_conf.get('bpm_change_chance', 0): 
        if not gen_conf.get('bpm_range'): 
            raise Exception('bpm_change_chance is set in conf, but bpm_range is set. If you want the BPM to change randomly, enable bpm_change_chance to the chance that each block will change the BPM, such as 0.15 for 15%, and set bpm_range to a range of values that it will choose from, such as range(250, 500, 50)')
        bpm_index = gen_conf['bpm_range'].index(block['block_data']['bpm'])
        bpm_change_limit = gen_conf.get('bpm_change_limit', 5)
        bpm_range = gen_conf['bpm_range'][bpm_index - bpm_change_limit : 1 + bpm_index + bpm_change_limit] or gen_conf['bpm_range']
        print 'Bpm range is : ', bpm_range

        new_bpm = random.choice(bpm_range)
    else: 
        new_bpm = block['block_data']['bpm']

    return new_bpm


def get_last_timing(base_block):
    if not base_block['block_data']['blocks']: 
        last_timing = {
            'starting_beats' : [0], 
            'number_of_bars' : 0,
            'bar_length' : 0
        }
    else:
        last_timing = base_block['block_data']['blocks'][-1]['structure_data']['timing_data']

    return last_timing

def get_chord_progression(number_of_bars):
    base_root = random.choice(chord_handler.base_notes)

    #Right now we just randomly choose from the configuration. Maybe have an AI to do this for us? 
    chord_choices = gen_conf.get('chord_choices', ['major', 'minor'])
    base_chord = random.choice(chord_choices)
    low_limit = gen_conf.get('lower_chord_diff_limit', 0)
    upper_limit = gen_conf.get('upper_chord_diff_limit', 10)

    chord_progression = chord_handler.make_chord_progression(base_root = base_root, base_chord = base_chord, number_of_chords = number_of_bars, chord_choices = chord_choices, lower_chord_diff_limit = low_limit, upper_chord_diff_limit = upper_limit)

    chords = []
    for i in range(number_of_bars):
        chord = chord_progression[i]
        notes_data = {
            'chord_root' : chord[0] + '3',
            'chord_type' : chord[1],
        }
        chords.append(notes_data)
    return chords

def base_block_timing(bar_timing, accents, base_block, number_of_repeats):
    bar_length, number_of_bars = bar_timing['bar_length'], bar_timing['number_of_bars']

    timing_data = {
                'starting_beats' : [i * number_of_bars * bar_length for i in range(number_of_repeats)],
                'bar_length' : bar_timing['bar_length'], 
                'number_of_bars' : bar_timing['number_of_bars'],
#                'base_volume' : base_volume,
                'accents' : accents,
                'max_note_len' : random.choice(gen_conf.get('max_note_len_range', [3])),
    }
    return timing_data

def generate_block(base_block, instrument_pool, bar_timing_gen):
    new_block = copy.deepcopy(block_template)

    #Right now we just randomly choose from the configuration. Maybe have an AI to do this for us? 
    bar_timing = next(bar_timing_gen)
    base_volume = random.choice(gen_conf.get('base_volume_range', range(40, 80, 10)))
    number_of_repeats = random.choice(gen_conf.get('number_of_repeats_range', [1]))
    number_block_occurences = random.choice(gen_conf.get('number_block_occurences_range', [1]))
    number_block_occurences = bar_timing['block_occurences']

    accents = {} #Temporary, don't even know how to make this work. 
#    chord_generator = block_chord_generator(len(instrument_pool))
    chord_progression = get_chord_progression(bar_timing['number_of_bars'])

    new_block['block_data']['bpm'] = get_block_bpm(base_block)
    new_block['block_data']['block_occurences'] = number_block_occurences
    new_block['block_data']['id'] = 'block_' + str(uuid.uuid4())[:8]
    new_block['structure_data']['timing_data'] = base_block_timing(bar_timing, accents, base_block, number_of_repeats)
    new_block['structure_data']['notes_data']['base_volume'] = gen_conf.get('base_volume', 30)



    for i in range(len(instrument_pool)):
        instrument = random.choice(instrument_pool)
        instrument = instrument_handler.get_instrument_data(instrument)

        #Channel 10 is reserved for percussions, so we shift all channels to the right. 
        #And to make it more confusing, channe 10 is in musical notations, so because it's 0-indexed here, really we want to have channel = 9 for percussions. 

        if i > 8: 
            i += 1

        block_instrument = {
            'block_data' : {
                'instrument' : instrument,
                'track' : i+1,
            }, 
            'structure_data' : {
                'timing_data' : {
#                    'starting_beats' : [i * bar_length * number_of_bars],
                    'number_of_bars' : bar_timing['number_of_bars']
                },
                'notes_data' : {
                    'chord_progression' : chord_progression,
                }
            }
        }
        new_block['block_data']['blocks'].append(block_instrument)


    return new_block

def get_percussion():
    number_of_percussion_tracks = gen_conf.get('percussion_tracks', 2)
    percussion = copy.deepcopy(percussion_block)
    percussion['block_data']['blocks'] *= number_of_percussion_tracks

    return percussion

def print_block_instruments(block):
    instrument_blocks = [x for x in block['block_data']['blocks'] if x['block_data'].get('instrument')]
    print 'Instruments for block at ', block['structure_data']['timing_data']['starting_beats'], ' are ', [x['block_data']['instrument']['instrument_name'] for x in instrument_blocks]

def bar_timing_generator(no_blocks):
    no_bars_initial = gen_conf.get('block_len_initial', 5)
    no_bars_range = [max(1, no_bars_initial - no_blocks), no_bars_initial + (no_blocks/2)]
    bar_len_initial = gen_conf.get('bar_len_initial', 15)

    get_occurences = lambda l, n: max(1, int(gen_conf.get('occurence_multiplier', 30) / float(l * n)))

    for b in range(no_blocks): 
        no_bars = random.randint(*no_bars_range)
#        bar_len_range = 3.0 / bar_len_initial - no_bars
        bar_len = int(bar_len_initial / float(no_bars))
#        bar_len = random.randint(*bar_len_range)
        occurences_range = [1, get_occurences(bar_len, no_bars)]
        number_occurences = occurences_range[-1]
        new_block_stats = {
            'number_of_bars' : no_bars, 
            'bar_length' : bar_len, 
            'block_occurences' : number_occurences,
        }
        yield new_block_stats

def generate_song():
    number_blocks_range = gen_conf.get('number_of_blocks_range', [1])
    print 'Choosing from ', number_blocks_range
    number_of_blocks = random.choice(number_blocks_range)
    base_block = copy.deepcopy(block_template)
    base_bpm = random.choice(gen_conf.get('bpm_range', [240]))
    base_block['block_data']['bpm'] = base_bpm
#    base_block['block_data']['bpm'] = int(base_bpm / (float(number_blocks_range[-1]) / number_of_blocks))
    print 'BPM is : ', base_block['block_data']['bpm']

    max_number_of_instruments = gen_conf.get('instrument_pool_range', range(4, 7))[-1]
    print 'Max number of instruments : ', max_number_of_instruments
    instrument_pool = [random.choice(gen_conf.get('instrument_pool', instrument_handler.get_list_of_instruments())) for i in range(max_number_of_instruments)]
    bar_timing_gen = bar_timing_generator(number_of_blocks)
    print 'Instrument pool is : ', instrument_pool
    for block in range(number_of_blocks):
        new_block = generate_block(base_block, instrument_pool, bar_timing_gen)
        percussion = get_percussion()
        new_block['block_data']['blocks'].append(percussion)
        base_block['block_data']['blocks'].append(new_block)

    base_block['block_data']['blocks'] = block_organizer.organize_blocks(base_block['block_data']['blocks'])

    for b in base_block['block_data']['blocks']: 
        print_block_instruments(b)

    song_name = get_name()
    song_path = gen_conf['song_path'] + get_name()
    block_parser.make_block_music(base_block, soundfont = gen_conf['soundfont'], song_name = song_path)

    return base_block


generate_song()
