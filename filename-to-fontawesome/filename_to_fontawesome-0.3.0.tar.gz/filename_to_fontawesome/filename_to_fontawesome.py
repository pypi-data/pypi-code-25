# -*- coding: utf-8 -*-

"""Main module."""
try:
    from .fontawesome import fontawesome
    from .fileextensions import (extensions, mimes)
except:
    from fontawesome import fontawesome
    from fileextensions import (extensions, mimes)


class ftfa:
    def __init__(self,
                 fontversion="v5regular",
                 markup=False,
                 prefa=True,
                 unicodeoutput=False):
        self.file_categories = (
            "word",
            "code",
            "video",
            "audio",
            "archive",
            "image",
            "powerpoint",
            "excel",
            "word",
            "pdf",
            "text")
        self.fontversion = fontversion
        self.markup = markup
        self.prefa = prefa
        self.unicodeoutput = unicodeoutput

    def getfontawesome(self, filename):
        category = "unknown"
        if '.' in filename:
            file_extension = filename.split('.')[-1]
            for cat in self.file_categories:
                if file_extension in getattr(extensions, cat)().get_types():
                    category = cat
                    break

        fv = getattr(fontawesome, self.fontversion)()
        if self.unicodeoutput:
            return fv.get_unicode(category, markup=self.markup)
        else:
            return fv.get(category, markup=self.markup, prefa=self.prefa)

    def mimetfa(self, mime):
        category = "unknown"
        for cat in self.file_categories:
            if mime in getattr(mimes, cat)().get_types():
                category = cat
                break

        fv = getattr(fontawesome, self.fontversion)()
        if self.unicodeoutput:
            return fv.get_unicode(category, markup=self.markup)
        else:
            return fv.get(category, markup=self.markup, prefa=self.prefa)
