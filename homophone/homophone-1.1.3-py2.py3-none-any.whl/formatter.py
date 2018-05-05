"""Output formatters"""

import click


class ConsoleFormatter:
    def __init__(self, show_genres):
        self.show_genres = show_genres

    def __call__(self, artist):
        s = artist.name
        if self.show_genres:
            g = "\n".join(map(lambda s: "\t" + s, artist.genres))
            s += "\n" + g
        return s
