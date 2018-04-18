from packrat.models import HoardFile
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse


def md5(request, hsh):
    hf = get_object_or_404(HoardFile, md5=hsh)

    def filedata():
        with open(hf.path, 'rb') as f:
            data = True
            while data:
                data = f.read(0x1000)
                yield data
    return StreamingHttpResponse(filedata(), content_type=hf.content_type)
