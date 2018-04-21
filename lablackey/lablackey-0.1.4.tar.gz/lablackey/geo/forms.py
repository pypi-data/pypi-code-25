from lablackey.forms import RequestModelForm
    
from .models import Location

class LocationForm(RequestModelForm):
  class Meta:
    model = Location
    fields = ('name','latlon','address','address2','city','zip_code',)
