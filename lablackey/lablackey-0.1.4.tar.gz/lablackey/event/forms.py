from lablackey.forms import RequestModelForm

from .models import EventOccurrence

class OccurrenceForm(RequestModelForm):
  class Meta:
    model = EventOccurrence
    fields = ('event','start','end_time')
