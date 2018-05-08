from generator.caches.base import SVGCache


class NoneCache(SVGCache):
    def get(self, parameters):
        return None

    def add(self, parameters, png_bytes):
        pass
