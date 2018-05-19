from hurriyet import errors


class ResultSet(list):
    """A list like object that holds results from a Hurriyet API query."""


class Model(object):
    _not_found_error_class = errors.NotFound

    def __init__(self, **kwargs):
        self._repr_values = ["id"]

    @classmethod
    def parse(cls, data, sub_item=False):
        data = data or {}
        if not data and not sub_item:
            raise cls._not_found_error_class()
        instance = cls() if data else None
        for key, value in data.items():
            if type(value) == str:
                value = value.strip()
            setattr(instance, key.lower(), value)
        return instance

    @classmethod
    def parse_list(cls, data, sub_item=False):
        """Parse a list of JSON objects into a result set of model instances."""
        results = ResultSet()
        data = data or []
        for obj in data:
            if obj:
                results.append(cls.parse(obj, sub_item=sub_item))
        return results

    def __repr__(self):
        items = filter(lambda x: x[0] in self._repr_values.keys(), vars(self).items())
        state = ['%s: %s' % (self._repr_values[k], repr(v)) for (k, v) in items]
        return '<%s: %s >' % (self.__class__.__name__, ', '.join(state))


class Article(Model):
    _not_found_error_class = errors.ArticleNotFound

    def __init__(self, **kwargs):
        super(Article, self).__init__(**kwargs)
        self._repr_values = {"id": "ID", "title": "Title"}


class Column(Model):
    _not_found_error_class = errors.ColumnNotFound

    def __init__(self, **kwargs):
        super(Column, self).__init__(**kwargs)
        self._repr_values = {"id": "ID", "title": "Title"}


class NewsPhotoGallery(Model):
    _not_found_error_class = errors.NewsPhotoGalleryNotFound

    def __init__(self, **kwargs):
        super(NewsPhotoGallery, self).__init__(**kwargs)
        self._repr_values = {"id": "ID", "title": "Title"}

    @classmethod
    def parse(cls, data, sub_item=False):
        news_photo_gallery = super(NewsPhotoGallery, cls).parse(data, sub_item=sub_item)
        if hasattr(news_photo_gallery, "files"):
            news_photo_gallery.files = File.parse_list(news_photo_gallery.files, sub_item=True)

        return news_photo_gallery


class File(Model):
    _not_found_error_class = errors.FileNotFound

    def __init__(self, **kwargs):
        super(File, self).__init__(**kwargs)
        self._repr_values = {"fileurl": "File Url"}

    @classmethod
    def parse(cls, data, sub_item=False):
        file = super(File, cls).parse(data, sub_item=sub_item)
        if hasattr(file, "metadata"):
            file.metadata = MetaData.parse(file.metadata, sub_item=True)

        return file


class MetaData(Model):
    _not_found_error_class = errors.MetaDataNotFound

    def __init__(self, **kwargs):
        super(MetaData, self).__init__(**kwargs)
        self._repr_values = {"title": "Title"}


class NewsVideo(Model):
    _not_found_error_class = errors.NewsVideoNotFound

    def __init__(self, **kwargs):
        super(NewsVideo, self).__init__(**kwargs)
        self._repr_values = {"id": "ID", "title": "Title"}

    @classmethod
    def parse(cls, data, sub_item=False):
        news_video = super(NewsVideo, cls).parse(data, sub_item=sub_item)
        if hasattr(news_video, "files"):
            news_video.files = File.parse_list(news_video.files, sub_item=True)

        return news_video


class Page(Model):
    _not_found_error_class = errors.PageNotFound

    def __init__(self, **kwargs):
        super(Page, self).__init__(**kwargs)
        self._repr_values = {"id": "ID", "title": "Title"}

    @classmethod
    def parse(cls, data, sub_item=False):
        page = super(Page, cls).parse(data, sub_item=sub_item)
        if hasattr(page, "pagenews"):
            page.pagenews = PageNews.parse_list(page.pagenews, sub_item=True)
        if hasattr(page, "folder"):
            page.folder = Folder.parse(page.folder, sub_item=True)

        return page


class PageNews(Model):
    _not_found_error_class = errors.PageNewsNotFound

    def __init__(self, **kwargs):
        super(PageNews, self).__init__(**kwargs)
        self._repr_values = {"id": "ID"}


class Folder(Model):
    _not_found_error_class = errors.FolderNotFound

    def __init__(self, **kwargs):
        super(Folder, self).__init__(**kwargs)
        self._repr_values = {"id": "ID", "title": "Title"}

    @classmethod
    def parse(cls, data, sub_item=False):
        folder = super(Folder, cls).parse(data, sub_item=sub_item)
        if hasattr(folder, "files"):
            folder.files = File.parse_list(folder.files, sub_item=True)

        return folder


class Path(Model):
    _not_found_error_class = errors.PathNotFound

    def __init__(self, **kwargs):
        super(Path, self).__init__(**kwargs)
        self._repr_values = {"id": "ID", "title": "Title"}


class Writer(Model):
    _not_found_error_class = errors.WriterNotFound

    def __init__(self, **kwargs):
        super(Writer, self).__init__(**kwargs)
        self._repr_values = {"id": "ID", "fullname": "Name"}

    @classmethod
    def parse(cls, data, sub_item=False):
        writer = super(Writer, cls).parse(data, sub_item=sub_item)
        if hasattr(writer, "files"):
            writer.files = File.parse_list(writer.files, sub_item=True)

        return writer
