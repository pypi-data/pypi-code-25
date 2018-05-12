from copy import copy

from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.conf import settings as thumbnailer_settings
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.templatetags.thumbnail import RE_SIZE, VALID_OPTIONS
from jinja2.exceptions import TemplateSyntaxError
from markupsafe import escape

from prometheus.template_backends.jinja2 import jinjafilter


@jinjafilter
def cropped_thumbnail(instance, field_name, width=None, height=None, scale=None, **kwargs):
    """Cropper"""
    thumbnail_options = copy(kwargs)
    ratiofield = instance._meta.get_field(field_name)
    image = getattr(instance, ratiofield.image_field)
    if ratiofield.image_fk_field:
        image = getattr(image, ratiofield.image_fk_field)
    if not image:
        return ''

    size = (int(ratiofield.width), int(ratiofield.height))
    box = getattr(instance, field_name)

    if scale:
        scale = float(scale)
        width = size[0] * scale
        height = size[1] * scale
    elif width and height:
        width = float(width)
        h = size[1] * width / size[0]
        if h > height:
            width = height * size[0] / size[1]
        else:
            height = h
    elif width:
        width = float(width)
        height = size[1] * width / size[0]
    elif height:
        height = float(height)
        width = height * size[0] / size[1]

    if width and height:
        size = (int(width), int(height))

    if ratiofield.adapt_rotation:
        if (image.height > image.width) != (size[1] > size[0]):
            size = (size[1], size[0])

    thumbnailer = get_thumbnailer(image)

    thumbnail_options.update({
        'size': size,
        'box': box
    })
    try:
        return thumbnailer.get_thumbnail(thumbnail_options).url
    except InvalidImageFormatError:
        return ''


@jinjafilter
def thumbnail_obj(source, size, **opts):
    """Make thumbnail from source image"""
    if not source:
        return None

    raise_errors = thumbnailer_settings.THUMBNAIL_DEBUG
    accepted_opts = {}
    for key, value in opts.items():
        if key in VALID_OPTIONS:
            accepted_opts[key] = value
    opts = accepted_opts
    m = RE_SIZE.match(size)

    if m:
        opts['size'] = (int(m.group(1)), int(m.group(2)))
    else:
        if raise_errors:
            raise TemplateSyntaxError('%r is not a valid size.' % size, 1)

    if 'quality' in opts:
        try:
            opts['quality'] = int(opts['quality'])
        except (TypeError, ValueError):
            if raise_errors:
                raise TemplateSyntaxError('%r is an invalid quality.' % opts['quality'], 1)

    try:
        curr_thumbnail = get_thumbnailer(source).get_thumbnail(opts)
    except Exception as e:
        if raise_errors:
            raise TemplateSyntaxError('Couldn\'t get the thumbnail %s: %s' % (source, e), 1)
        else:
            return None

    return curr_thumbnail


@jinjafilter
def thumbnail(source, size, **opts):
    thumb = thumbnail_obj(source, size, **opts)
    return escape(thumb.url) if thumb else ''
