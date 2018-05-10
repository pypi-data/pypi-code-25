import datetime
import hashlib
import os

from PIL import Image
from django import http
from django.conf import settings
from django.utils.text import slugify
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

REDACTOR = getattr(settings, 'REDACTOR_SETTINGS', {})
UPLOAD_ROOT = REDACTOR.get('upload_root', os.path.join(settings.MEDIA_ROOT, 'uploads'))
UPLOAD_URL = REDACTOR.get('upload_url', settings.MEDIA_URL + 'uploads/')


def handle_uploaded_file(f, filename, folder):
    name, ext = os.path.splitext(slugify(filename).replace(' ', '_'))
    hashed_name = hashlib.md5(
        (name + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
         ).encode('utf8')).hexdigest()
    new_filename = hashed_name + ext

    path_dir = os.path.join(UPLOAD_ROOT, folder)
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    path_name = os.path.join(path_dir, new_filename)
    with open(path_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return os.path.join(folder, new_filename)


@staff_member_required
@csrf_exempt
def upload_img(request):
    if request.method == 'POST':
        path = handle_uploaded_file(request.FILES['file'],
                                    request.FILES['file'].name, 'images/')
        url = os.path.join(UPLOAD_URL, path)
        size = (650, 650)
        full_path = os.path.join(UPLOAD_ROOT, path)
        im = Image.open(full_path)
        image_size = im.size
        if (image_size[0] > size[0]) or (image_size[1] > size[1]):
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(full_path, "JPEG", quality=100)
        return HttpResponse('{"filelink":"%s"}' % url)
    else:
        return HttpResponse('error')


@staff_member_required
@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        path = handle_uploaded_file(request.FILES['file'],
                                    request.FILES['file'].name, 'files/')
        url = os.path.join(UPLOAD_URL, path)
        response_data = '{"filelink":"%s","filename":"%s"}' % (
            url, request.FILES['file'].name)
        return HttpResponse(response_data)
