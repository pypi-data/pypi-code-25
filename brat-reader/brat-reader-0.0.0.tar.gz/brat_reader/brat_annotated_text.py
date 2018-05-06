from collections import defaultdict
import t4k
from copy import deepcopy

def count_attributions(annotation_text):
    return len([
        line for line in annotation_text.split('\n') if line.startswith('E')
    ])


class BratAnnotatedText(object):


    def __init__(self, annotation_text=None, events=None, spans=None):
        if annotation_text is not None:
            self.events = {}
            self.spans = {}
            self.all_span_ids = set()
            self.parse(annotation_text)
        elif events is not None and spans is not None:
            self.events = deepcopy(events)
            self.spans = deepcopy(spans)
            self.all_span_ids = set(self.spans.keys())
        else:
            raise ValueError(
                'Must specify either annotation_text or events and spans')

        self.make_events_by_span()
        self.validate()


    def make_events_by_span(self):
        self.events_by_span = defaultdict(list)
        for event_id, spans in self.events.iteritems():
            for role, span_id in spans:
                self.events_by_span[span_id].append(event_id)


    def parse(self, annotation_text):
        lines = annotation_text.split('\n')
        for line in t4k.skip_blank(lines):
            if line.startswith('T'):
                self.parse_span(line)
            elif line.startswith('E'):
                self.parse_event(line)
            elif line.startswith('#'):  # Signals an annotator comment
                pass
            else:
                print line
                raise ValueError('Malformed annotation text')

    def get_event_specs(self):

        # Within event specs, replace the span identifier with the range spec
        # for the span.
        finalized_event_specs = {
            event_id: {
                span_type.lower(): self.spans[span_id][1]
                for span_type, span_id in event
            }
            for event_id, event in self.events.iteritems()
        }
        return finalized_event_specs


    def parse_span(self, line):

        # Every entry has a span_id, followed by a specification
        span_id, spec = line.split('\t', 1)

        # The span's spec consists of a role and range spec separated by a
        # tab from a listing of the tokens under that range.  We don't want
        # the token literals, just the role and range spec.
        role_and_range_specs = spec.split('\t')[0]
        role, range_specs = role_and_range_specs.split(' ', 1)

        # The ranges are like `start end:start end:...`
        # Separate individual ranges, parse out the start and endpoint for 
        # each (converting them to ints)
        ranges = tuple([
            tuple([int(i) for i in r.split(' ')]) 
            for r in range_specs.split(';')
        ])
        self.spans[span_id] = (role.lower(), ranges)


    def parse_event(self, line):

        # Every entry has a event_id, followed by a specification
        event_id, spec = line.split('\t', 1)

        # The event spec has several role:event_id words separated by 
        # spaces.  The "Source", "Cue", and "Content" roles are of interest
        # but the "Attribution" role is redundant so we filter it out.
        event = [
            (s.split(':')[0].lower(), s.split(':')[1])
            for s in spec.split()
        ]
        self.events[event_id] = event


    def validate(self):

        event_errors = defaultdict(list)
        seen_cues, seen_contents, seen_sources = set(), set(), set()

        # Check that each event has the correct components.
        for event_id, event in self.events.items():

            # Check the cue
            if not 'cue' in event:
                event_errors[event_id].append('no cue')
            else:
                seen_cues.add(event['cue'])
                if not event['cue'] in self.spans['cue']:
                    event_errors[event_id].append('bad cue')

            # Check the content
            if not 'content' in event:
                event_errors[event_id].append('no content')
            else:
                seen_contents.add(event['content'])
                if not event['content'] in self.spans['content']:
                    event_errors[event_id].append('bad content')

            # Check the source (if any)
            if 'source' in event:
                seen_sources.add(event['source'])
                if not event['source'] in self.spans['source']:
                    event_errors[event_id].append('bad source')

        # Check for dangling spans
        all_seen_spans = seen_sources | seen_contents | seen_cues
        dangling_spans = self.all_span_ids - all_seen_spans

        self.validation = {
            'event_errors': event_errors,
            'dangling_spans': dangling_spans
        }

