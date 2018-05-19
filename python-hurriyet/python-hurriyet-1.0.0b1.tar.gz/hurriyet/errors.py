import six


class HurriyetError(Exception):
    message = six.text_type("Unknown error")

    def __init__(self, message=None, status=None):
        self.message = six.text_type(message) if message else self.message
        self.status = status
        super(HurriyetError, self).__init__(message, status)

    def __str__(self):
        return self.message


class ConnectionError(HurriyetError):
    pass


class NotFound(HurriyetError):
    message = six.text_type(u"Not Found")


class ArticleNotFound(NotFound):
    message = six.text_type(u"Article Not Found")


class ColumnNotFound(NotFound):
    message = six.text_type(u"Column Not Found")


class NewsPhotoGalleryNotFound(NotFound):
    message = six.text_type(u"News Photo Gallery Not Found")


class FileNotFound(NotFound):
    message = six.text_type(u"File Not Found")


class MetaDataNotFound(NotFound):
    message = six.text_type(u"Meta Data Not Found")


class NewsVideoNotFound(NotFound):
    message = six.text_type(u"News Video Not Found")


class PageNotFound(NotFound):
    message = six.text_type(u"Page Not Found")


class PageNewsNotFound(NotFound):
    message = six.text_type(u"Page News Not Found")


class FolderNotFound(NotFound):
    message = six.text_type(u"Folder Not Found")


class PathNotFound(NotFound):
    message = six.text_type(u"Path Not Found")


class WriterNotFound(NotFound):
    message = six.text_type(u"Writer Not Found")
