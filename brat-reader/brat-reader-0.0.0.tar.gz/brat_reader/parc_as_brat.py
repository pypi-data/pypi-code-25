import brat_reader


def get_parc_as_brat(parc_instance):

    attributions = {}
    spans = {}
    span_id_generator = IdGenerator('T')
    event_id_generator = IdGenerator('E')
    for attr in parc_instance.attributions.values():
        new_attribution = []
        event_id = event_id_generator.get_next_id()
        attributions[event_id] = new_attribution

        if len(attr['source']) > 1:
            span_id = span_id_generator.get_next_id()
            spans[span_id] = ('source', span_tokens_to_ranges(attr['source']))
            new_attribution.append(('source', span_id))

        span_id = span_id_generator.get_next_id()
        spans[span_id] = ('cue', span_tokens_to_ranges(attr['cue']))
        new_attribution.append(('cue', span_id))

        span_id = span_id_generator.get_next_id()
        spans[span_id] = ('content', span_tokens_to_ranges(attr['content']))
        new_attribution.append(('content', span_id))

    return brat_reader.BratAnnotatedText(events=attributions, spans=spans)



class IdGenerator(object):
    
    def __init__(self, prefix):
        self._cur_id = 0
        self._prefix = prefix

    def get_next_id(self):
        self._cur_id += 1
        return self._prefix + str(self._cur_id)



def span_tokens_to_ranges(span_tokens):
    ranges = []
    last_token = None
    last_token_id = None
    last_sentence_id = None
    start = None
    end = None
    for token in span_tokens:
        token_id = token['id']
        sentence_id = token['sentence_id']

        # The first span is started here
        if last_token_id is None:
            start = token['character_offset_begin']

        # The current span ends, and a new one begins, when the sentence id
        # doesn't match, or when the tokens aren't consecutive
        elif last_token_id != token_id - 1:
            end = last_token['character_offset_end']
            ranges.append((start, end))
            start = token['character_offset_begin']
            end = None

        last_token = token
        last_token_id = token_id
        last_sentence_id = sentence_id

    if start is not None:
        end = last_token['character_offset_end']
        ranges.append((start, end))

    return ranges


