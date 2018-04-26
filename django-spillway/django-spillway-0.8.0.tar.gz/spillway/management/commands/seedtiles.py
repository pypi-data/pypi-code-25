import sys
import itertools
import socket

from django.utils.six.moves.http_client import HTTPException
from django.utils.six.moves.urllib.error import URLError
from django.utils.six.moves.urllib.parse import urlunparse
from django.utils.six.moves.urllib.request import urlopen

from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.urls import reverse, NoReverseMatch
from django.utils.module_loading import import_string
from greenwich import tile, srs, Envelope


class Tiler(object):
# class TileSeeder(object):
# class TileRequest(s)(object):
    # def __init__(self, extent, zlevs, stderr=None):
    # def __init__(self, extent, zlevs, command=None):
    # def __init__(self, baseurl, tiles, command=None):
    def __init__(self, baseurl, tiles):
        # if len(baseurl) != 6:
            # raise ValueError('URL must be 6-length sequence')
        # self.baseurl = baseurl
        try:
            # url = urlparse.urlunparse(baseurl)
            url = urlunparse(baseurl)
            self.baseurl = baseurl
        except ValueError as exc:
            exc.args = ('URL must be 6-length sequence',)
            raise
        # self.tiles = tile_coords(extent, zlevs)
        self.tiles = tiles
        # FIXME: clean this up
        # self.stdout = sys.stdout
        # self.stderr = sys.stderr
        # self.cmd = command
        # self.urls = []
        self.format = 'png'
        self.tileview = 'raster-tiles'

    def _build_url(self, kwargs):
        try:
            urlpath = reverse(self.tileview, kwargs=kwargs)
        except NoReverseMatch as exc:
            raise CommandError(exc.message)
        # urlargs = ['', options['host'], urlpath, '', options['params'], '']
        # urlargs = (options['scheme'], options['host'], urlpath, '',
                   # options['params'], '')
        urlargs = list(self.baseurl)
        urlargs[2] = urlpath
        url = urlparse.urlunparse(urlargs)
        return url

    # def request_tiles(self, obj, options):
    def request_tiles(self, obj):
        for tile in self.tiles:
            # self.cmd.stdout.write('TILE z: %s, x: %s, y: %s' % tile)
            kwargs = dict(zip(('z', 'x', 'y'), tile),
                          slug=obj.slug, format=self.format)
            # url = self._build_url(obj.slug)
            url = self._build_url(kwargs)
            # self.cmd.stdout.write('Request: %s' % url)
            sys.stdout.write('Request: %s' % url)
            self._make_request(url)

    def _make_request(self, url):
        try:
            # fp = urllib2.urlopen(url)
            fp = urlopen(url)
            print(fp.headers.dict)
        # TODO: Straighten out errors, more generic exc?
        # except urllib2.HTTPError as exc:
        # except urllib2.URLError as exc:
        except URLError as exc:
            # self.cmd.stderr.write(self.cmd.style.ERROR(str(exc)))
            # self.cmd.stderr.write(self.cmd.style.ERROR('%s: "%s"' % (exc, url)))
            sys.stderr.write(self.cmd.style.ERROR('%s: "%s"' % (exc, url)))
        except HTTPException as exc:
            # self.cmd.stderr.write(self.cmd.style.ERROR('XFailed: "%s"' % exc))
            sys.stderr.write(self.cmd.style.ERROR('XFailed: "%s"' % exc))
        except socket.timeout as exc:
            # self.cmd.stderr.write(self.cmd.style.ERROR('Failed: "%s"' % exc))
            sys.stderr.write(self.cmd.style.ERROR('Failed: "%s"' % exc))
        # except (httplib.HTTPException, socket.timeout, urllib2.URLError) as exc:
            # self.cmd.stderr.write(self.cmd.style.ERROR(str(exc)))
        else:
            fp.close()

# tilestache-seed.py -c ./config.json -l osm -b 37.79 -122.35 37.83 -122.25 -e png 12 13 14 15
class Command(BaseCommand):
    help = 'Preseed a tile cache'

    # TODO: Need (opt)args for ModelName, view-name, slug/layer, bbox, format
    def add_arguments(self, parser):
        parser.add_argument('model')
        # parser.add_argument('slug')
        parser.add_argument('zoom_levels', nargs='+', type=int)
        parser.add_argument(
            # '-L', '--layer-slug',
            '-s', '--slug',
            # help='Layer slug',
        )
        # parser.add_argument(
            # '--model',
            # help='Model',
        # )
        parser.add_argument('-H', '--host', default='localhost')
        parser.add_argument('-S', '--scheme', default='http')
        parser.add_argument('-p', '--params')
        # parser.add_argument('-q', '--query')
        # concurrent requests
        # parser.add_argument('-j', '--jobs')

    def handle(self, *args, **options):
        try:
            model = import_string(options['model'])
        except ImportError:
            raise CommandError('Cannot import Model: "%s"' % options['model'])
        qs = model.objects.all()
        print('ARGS:', args)
        print('OPTIONS:', options)
        if options['slug']:
            qs = qs.filter(slug=options['slug'])
        if not qs.count():
            # raise CommandError('No results for slug: "%s"' % options['slug'])
            raise CommandError('Empty QuerySet for "%s"' % model)
        # slug = 'slr_sfbay_0_0m_jdr'
        # qs = qs.filter(slug=slug)
        for obj in qs:
            # list_tiles()
            tiles = tile.from_bbox(obj.geom.extent, options['zoom_levels'])
            # self.request_tiles(obj, tiles, options)
            urlargs = (options['scheme'], options['host'], '', '',
                       options['params'], '')
            t = Tiler(urlargs, tiles, command=self)
            # t = Tiler(urlargs, obj.geom.extent,
                      # options['zoom_levels'], command=self)
            t.request_tiles(obj)
