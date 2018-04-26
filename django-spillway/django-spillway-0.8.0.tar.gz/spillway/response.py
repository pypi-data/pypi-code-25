from django.http import HttpResponse


class MapnikResponse(HttpResponse):
    # media_types = {'png': 'image/png'}
    # def __init__(self, content, *args, **kwargs):
    # def __init__(self, mapobj, renderer, *args, **kwargs):
    def __init__(self, mapobj, renderer, **kwargs):
        kwargs.setdefault('content_type', renderer.media_type)
        super(MapnikResponse, self).__init__(
            content=mapobj.render(renderer.format), **kwargs)
