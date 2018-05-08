from generator.caches.base import SVGCache


class LocalCache(SVGCache):
    def __init__(self):
        self._renders = []

    def get(self, parameters):
        for (p, buffer) in self._renders:
            if parameters == p:
                return buffer
        return None

    def add(self, parameters, png_bytes):
        self._renders.append((parameters, png_bytes))
