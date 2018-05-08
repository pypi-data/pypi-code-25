import pystache
from cairosvg.surface import PNGSurface

from generator.caches.none import NoneCache


class SVGenerator:
    """
    Fast and cached PNG generation from Mustache SVG templates
    """

    def __init__(self, svg_template, cache=NoneCache()):
        """
        :param svg_template: the Mustache SVG template
        :param cache: the cache to use.
        """
        self._svg_template = svg_template

        if cache is None:
            cache = NoneCache()
        self._cache = cache

    def render(self, parameters):
        """
        Render the SVG template with passed parameters as PNG
        Will try to read from cache if possible. Will put the render in cache if it was not found.
        :param parameters: the parameters
        :return: the computed PNG as bytestring
        """
        cached_value = self._cache.get(parameters)
        if cached_value:
            return cached_value

        svg = pystache.render(self._svg_template, parameters)
        png_buffer = PNGSurface.convert(bytestring=svg)
        self._cache.add(parameters, png_buffer)
        return png_buffer

    def render_to_file(self, parameters, path):
        """
        Same as render, but writes result to file instead of returning bytestring
S        """
        with open(path, 'wb') as f:
            f.write(self.render(parameters))

    @staticmethod
    def from_file(path, cache=None):
        with open(path, 'rb') as f:
            return SVGenerator.from_str(f.read(), cache=cache)

    @staticmethod
    def from_str(s, cache=None):
        return SVGenerator(s, cache=cache)
