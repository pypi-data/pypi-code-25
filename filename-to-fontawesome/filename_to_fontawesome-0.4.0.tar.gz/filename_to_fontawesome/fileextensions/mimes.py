import abc


class mimes(object):
    """
    Metaclass to retrieve mimes by category
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_types(self):
        pass


class text(mimes):
    """
    Mime types for text files
    """

    def __init__(self):
        """
        Takes no argument
        Build tuple of mimes types for text files
        """
        self.types = (
            'text/plain',
        )

    def get_types(self):
        """
        Takes no argument
        Returns mimes of types for text files
        """
        return self.types


class word(mimes):
    """
    Mime types for word files
    """

    def __init__(self):
        """
        Takes no argument
        Build tuple of mimes types for word files
        """
        self.types = ('application/msword',)

    def get_types(self):
        """
        Takes no argument
        Returns tuple of mimes types for word files
        """
        return self.types


class code(mimes):
    """
    Mime types for files containing code
    """

    def __init__(self):
        """
        Takes no argument
        Build tuple of mimes types for files containing code
        """
        self.types = (
            'text/asp',
            'text/css',
            'text/ecmascript',
            'text/html',
            'text/javascript',
            'text/mcf',
            'text/pascal',
            'text/richtext',
            'text/scriplet',
            'text/sgml',
            'text/tab-separated-values',
            'text/uri-list',
            'text/vnd.abc',
            'text/vnd.fmi.flexstor',
            'text/vnd.rn-realtext',
            'text/vnd.wap.wml',
            'text/vnd.wap.wmlscript',
            'text/webviewhtml',
            'text/x-asm',
            'text/x-audiosoft-intra',
            'text/x-c',
            'text/x-component',
            'text/x-fortran',
            'text/x-h',
            'text/x-java-source',
            'text/x-la-asf',
            'text/x-m',
            'text/x-pascal',
            'text/x-script',
            'text/x-script.csh',
            'text/x-script.elisp',
            'text/x-script.guile',
            'text/x-script.ksh',
            'text/x-script.lisp',
            'text/x-script.perl',
            'text/x-script.perl-module',
            'text/x-script.phyton',
            'text/x-script.rexx',
            'text/x-script.scheme',
            'text/x-script.sh',
            'text/x-script.tcl',
            'text/x-script.tcsh',
            'text/x-script.zsh',
            'text/x-server-parsed-html',
            'text/x-setext',
            'text/x-sgml',
            'text/x-speech',
            'text/x-uil',
            'text/x-uuencode',
            'text/x-vcalendar',
            'text/xml',
        )

    def get_types(self):
        """
        Takes no argument
        Returns tuple of mimes types for files containing code
        """
        return self.types


class video(mimes):
    """
    Mime types for video files
    """

    def __init__(self):
        """
        Takes no argument
        Build tuple of mimes types for video files
        """
        self.types = (
            'video/animaflex',
            'video/avi',
            'video/avs-video',
            'video/dl',
            'video/fli',
            'video/gl',
            'video/mpeg',
            'video/msvideo',
            'video/quicktime',
            'video/vdo',
            'video/vivo',
            'video/vnd.rn-realvideo',
            'video/vnd.vivo',
            'video/vosaic',
            'video/x-amt-demorun',
            'video/x-amt-showrun',
            'video/x-atomic3d-feature',
            'video/x-dl',
            'video/x-dv',
            'video/x-fli',
            'video/x-gl',
            'video/x-isvideo',
            'video/x-motion-jpeg',
            'video/x-mpeg',
            'video/x-mpeq2a',
            'video/x-ms-asf',
            'video/x-ms-asf-plugin',
            'video/x-msvideo',
            'video/x-qtc',
            'video/x-scm',
            'video/x-sgi-movie',
        )

    def get_types(self):
        """
        Takes no argument
        Returns mimes of types for video files
        """
        return self.types


class audio(mimes):
    """
    Mime types for audio files
    """

    def __init__(self):
        """
        Takes no argument
        Build tuple of mimes types for audio files
        """
        self.types = (
            'audio/aiff',
            'audio/basic',
            'audio/it',
            'audio/make',
            'audio/make.my.funk',
            'audio/mid',
            'audio/midi',
            'audio/mod',
            'audio/mpeg',
            'audio/mpeg3',
            'audio/nspaudio',
            'audio/s3m',
            'audio/tsp-audio',
            'audio/tsplayer',
            'audio/vnd.qcelp',
            'audio/voc',
            'audio/voxware',
            'audio/wav',
            'audio/x-adpcm',
            'audio/x-aiff',
            'audio/x-au',
            'audio/x-gsm',
            'audio/x-jam',
            'audio/x-liveaudio',
            'audio/x-mid',
            'audio/x-midi',
            'audio/x-mod',
            'audio/x-mpeg',
            'audio/x-mpeg-3',
            'audio/x-mpequrl',
            'audio/x-nspaudio',
            'audio/x-pn-realaudio',
            'audio/x-pn-realaudio-plugin',
            'audio/x-psid',
            'audio/x-realaudio',
            'audio/x-twinvq',
            'audio/x-twinvq-plugin',
            'audio/x-vnd.audioexplosion.mjuicemediafile',
            'audio/x-voc',
            'audio/x-wav',
            'audio/xm',
        )

    def get_types(self):
        """
        Takes no argument
        Returns mimes of types for audio files
        """
        return self.types


class archive(mimes):
    """
    Mime types for archive files
    """

    def __init__(self):
        """
        Takes no argument
        Build tuple of mimes types for archive files
        """
        self.types = (
            'application/x-compressed',
            'application/x-zip-compressed',
            'application/x-bzip',
            'application/x-bzip2',
            'application/x-gzip',
            'application/zip',
            'multipart/x-gzip',
            'multipart/x-zip',
        )

    def get_types(self):
        """
        Takes no argument
        Returns mimes of types for archive files
        """
        return self.types


class image(mimes):
    """
    Mime types for image files
    """

    def __init__(self):
        """
        Takes no argument
        Build tuple of mimes types for image files
        """
        self.types = (
            'image/bmp',
            'image/cmu-raster',
            'image/fif',
            'image/florian',
            'image/g3fax',
            'image/gif',
            'image/ief',
            'image/jpeg',
            'image/jutvision',
            'image/naplps',
            'image/pict',
            'image/pjpeg',
            'image/png',
            'image/tiff',
            'image/vasa',
            'image/vnd.dwg',
            'image/vnd.fpx',
            'image/vnd.net-fpx',
            'image/vnd.rn-realflash',
            'image/vnd.rn-realpix',
            'image/vnd.wap.wbmp',
            'image/vnd.xiff',
            'image/x-cmu-raster',
            'image/x-dwg',
            'image/x-icon',
            'image/x-jg',
            'image/x-jps',
            'image/x-niff',
            'image/x-pcx',
            'image/x-pict',
            'image/x-portable-anymap',
            'image/x-portable-bitmap',
            'image/x-portable-graymap',
            'image/x-portable-greymap',
            'image/x-portable-pixmap',
            'image/x-quicktime',
            'image/x-rgb',
            'image/x-tiff',
            'image/x-windows-bmp',
            'image/x-xbitmap',
            'image/x-xbm',
            'image/x-xpixmap',
            'image/x-xwd',
            'image/x-xwindowdump',
            'image/xbm',
            'image/xpm',
        )

    def get_types(self):
        """
        Takes no argument
        Returns mimes of types for image files
        """
        return self.types


class powerpoint(mimes):
    """
    Mime types for powerpoint files
    """

    def __init__(self):
        """
        Takes no argument
        Build tuple of mimes types for powerpoint files
        """
        self.types = (
            'application/mspowerpoint',
            'application/x-mspowerpoint',
        )

    def get_types(self):
        """
        Takes no argument
        Returns mimes of types for powerpoint files
        """
        return self.types


class excel(mimes):
    """
    Mime types for excel files
    """

    def __init__(self):
        """
        Takes no argument
        Build tuple of mimes types for excel files
        """
        self.types = (
            'application/excel',
            'application/x-excel',
            'application/x-msexcel',
        )

    def get_types(self):
        """
        Takes no argument
        Returns mimes of types for excel files
        """
        return self.types


class pdf(mimes):
    """
    Mime types for pdf files
    """

    def __init__(self):
        """
        Takes no argument
        Build tuple of mimes types for pdf files
        """
        self.types = ('application/pdf',)

    def get_types(self):
        """
        Takes no argument
        Returns mimes of types for pdf files
        """
        return self.types
