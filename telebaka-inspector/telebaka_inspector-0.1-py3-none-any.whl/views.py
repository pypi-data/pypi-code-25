from django.http import JsonResponse, HttpResponse
from django.views.generic import DetailView

from telebaka_inspector.models import Message


class InspectorView(DetailView):
    model = Message

    def render_to_response(self, context, **response_kwargs):
        return HttpResponse(self.object.message_json, content_type='application/json')
