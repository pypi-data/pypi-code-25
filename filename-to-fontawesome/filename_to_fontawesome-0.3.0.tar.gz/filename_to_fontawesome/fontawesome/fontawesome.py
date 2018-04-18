import abc
from collections import namedtuple


class fontawesome(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        self.fontawesomedict = namedtuple(
            'fontawesome',
            '''
            unknown
            word
            code
            video
            audio
            archive
            image
            powerpoint
            excel
            pdf
            text
            medical
            meficalalt
            ''')
        self.icon = namedtuple('icon', '''string unicode''')

    @abc.abstractmethod
    def get(self, filetype, markup=False, prefa=True):
        pass

    @abc.abstractmethod
    def get_unicode(self, filetype, markup=False):
        pass


class v4(fontawesome):
    def __init__(self):
        super(v4, self).__init__()
        self.fa4 = self.fontawesomedict(
            self.icon("file-o", "f016"),
            self.icon("file-word-o", "f1c2"),
            self.icon("file-code-o", "f1c9"),
            self.icon("file-video-o", "f1c8"),
            self.icon("file-audio-o", "f1c7"),
            self.icon("file-archive-o", "f1c6"),
            self.icon("file-image-o", "f1c5"),
            self.icon("file-powerpoint-o", "f1c4"),
            self.icon("file-excel-o", "f1c3"),
            self.icon("file-pdf-o", "f1c1"),
            self.icon("file-text-o", "f15c"),
            self.icon("file-o", "f016"),
            self.icon("file-o", "f016")
        )

    def get(self, filetype, markup=False, prefa=True):
        fa = getattr(self.fa4, filetype)
        if markup:
            return """<i class="fa fa-{}" aria-hidden="true"></i>""".format(
                fa.string)
        if prefa:
            return """fa fa-{}""".format(fa.string)
        else:
            return """fa-{}""".format(fa.string)

    def get_unicode(self, filetype, markup=False):
        fa = getattr(self.fa4, filetype)
        return """{}""".format(fa.unicode)


class v5regular(fontawesome):
    def __init__(self):
        super(v5regular, self).__init__()
        self.fa5regular = self.fontawesomedict(
            self.icon("file", "f15b"),
            self.icon("file-word", "f1c2"),
            self.icon("file-code", "f1c9"),
            self.icon("file-video", "f1c8"),
            self.icon("file-audio", "f1c7"),
            self.icon("file-archive", "f1c6"),
            self.icon("file-image", "f1c5"),
            self.icon("file-powerpoint", "f1c4"),
            self.icon("file-excel", "f1c3"),
            self.icon("file-pdf", "f1c1"),
            self.icon("file-text", "f15c"),
            self.icon("file-medical", "f477"),
            self.icon("file-medical-alt", "f478")
        )

    def get(self, filetype, markup=False, prefa=True):
        fa = getattr(self.fa5regular, filetype)
        if markup:
            return """<i class="far fa-{}"></i>""".format(fa.string)
        if prefa:
            return """far fa-{}""".format(fa.string)
        else:
            return """fa-{}""".format(fa.string)

    def get_unicode(self, filetype, markup=False):
        fa = getattr(self.fa5regular, filetype)
        return """{}""".format(fa.unicode)


class v5solid(fontawesome):
    def __init__(self):
        super(v5solid, self).__init__()
        self.fa5solid = self.fontawesomedict(
            self.icon("file", "f15b"),
            self.icon("file-word", "f1c2"),
            self.icon("file-code", "f1c9"),
            self.icon("file-video", "f1c8"),
            self.icon("file-audio", "f1c7"),
            self.icon("file-archive", "f1c6"),
            self.icon("file-image", "f1c5"),
            self.icon("file-powerpoint", "f1c4"),
            self.icon("file-excel", "f1c3"),
            self.icon("file-pdf", "f1c1"),
            self.icon("file-text", "f15c"),
            self.icon("file-medical", "f477"),
            self.icon("file-medical-alt", "f478")
        )

    def get(self, filetype, markup=False, prefa=True):
        fa = getattr(self.fa5solid, filetype)
        if markup:
            return """<i class="fas fa-{}"></i>""".format(fa.string)
        if prefa:
            return """fas fa-{}""".format(fa.string)
        else:
            return """fa-{}""".format(fa.string)

    def get_unicode(self, filetype, markup=False):
        fa = getattr(self.fa5solid, filetype)
        return """{}""".format(fa.unicode)
