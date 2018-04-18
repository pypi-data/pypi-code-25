import abc


class extensions(object):
    """
    Metaclass for Extensions
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, arg):
        pass

    @abc.abstractmethod
    def get_types(self):
        pass


class text(extensions):
    """
    Extensions for text files
    """

    def __init__(self):
        """
        Takes no argument
        Builds tuple containing text files extensions
        """
        self.types = (
            "txt", "st", "md")

    def get_types(self):
        """
        Takes no argument
        Returns tuple for text file extensions
        """
        return self.types


class word(extensions):
    """
    Extensions for word files
    """

    def __init__(self):
        """
        Takes no argument
        Builds tuple containing word files extensions
        """
        self.types = ("doc", "docx", "odt")

    def get_types(self):
        """
        Takes no argument
        Returns tuple for word file extensions
        """
        return self.types


class code(extensions):
    """
    Extensions for code files
    """

    def __init__(self):
        """
        Takes no argument
        Builds tuple containing code files extensions
        """
        self.types = (
            "py", "rs", "go", "c",
            "java", "js", "html", "css",
            "json"
        )

    def get_types(self):
        """
        Takes no argument
        Returns tuple for code file extensions
        """
        return self.types


class video(extensions):
    """
    Extensions for video files
    """

    def __init__(self):
        """
        Takes no argument
        Builds tuple containing video files extensions
        """
        self.types = (
            "mp4", "m4v", "mkv", "webm",
            "mov", "avi", "wmv", "mpg",
            "flv", "webm"
        )

    def get_types(self):
        """
        Takes no argument
        Returns tuple for video file extensions
        """
        return self.types


class audio(extensions):
    """
    Extensions for audio files
    """

    def __init__(self):
        """
        Takes no argument
        Builds tuple containing audio files extensions
        """
        self.types = (
            "mid", "mp3", "m4a", "ogg",
            "flac", "wav", "amr",
        )

    def get_types(self):
        """
        Takes no argument
        Returns tuple for audio file extensions
        """
        return self.types


class archive(extensions):
    """
    Extensions for archive files
    """

    def __init__(self):
        """
        Takes no argument
        Builds tuple containing archive files extensions
        """
        self.types = (
            "epub", "zip", "tar", "rar",
            "gz", "bz2", "7z", "xz",
            "exe", "swf", "rtf", "eot",
            "ps", "sqlite", "nes", "crx",
            "cab", "deb", "ar", "Z", "lz",
        )

    def get_types(self):
        """
        Takes no argument
        Returns tuple for archive file extensions
        """
        return self.types


class image(extensions):
    """
    Extensions for image files
    """

    def __init__(self):
        """
        Takes no argument
        Builds tuple containing image files extensions
        """
        self.types = (
            "ani", "bmp", "cal", "fax",
            "gif", "img", "jbg", "jpe",
            "jpeg", "jpg", "mac", "pbm",
            "pcd", "pcx", "pct", "pgm",
            "png", "ppm", "psd", "ras",
            "tga", "tiff", "wmf",
        )

    def get_types(self):
        """
        Takes no argument
        Returns tuple for image file extensions
        """
        return self.types


class powerpoint(extensions):
    """
    Extensions for powerpoint files
    """

    def __init__(self):
        """
        Takes no argument
        Builds tuple containing powerpoint files extensions
        """
        self.types = ("pptx", "ppt")

    def get_types(self):
        """
        Takes no argument
        Returns tuple for powerpoint file extensions
        """
        return self.types


class excel(extensions):
    """
    Extensions for excel files
    """

    def __init__(self):
        """
        Takes no argument
        Builds tuple containing excel files extensions
        """
        self.types = (
            "xlsx", "xls", "csv", "lxsx",
            "ods")

    def get_types(self):
        """
        Takes no argument
        Returns tuple for excel file extensions
        """
        return self.types


class pdf(extensions):
    """
    Extensions for pdf files
    """

    def __init__(self):
        """
        Takes no argument
        Builds tuple containing pdf files extensions
        """
        self.types = ("pdf")

    def get_types(self):
        """
        Takes no argument
        Returns tuple for pdf file extensions
        """
        return self.types
