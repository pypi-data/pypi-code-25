from __future__ import absolute_import
from datetime import datetime, timedelta

import os
import xml.etree.ElementTree as ET

from anidb import urls
from anidb.helper import parse_date, data_fetch, download_file
import anidb.compat as compat


class Anime(object):

    def __init__(self, anidb, id, auto_load=True, xml=None,
                 url_http_api=urls.URL_HTTP_API, url_image_host=urls.URL_IMAGE_HOST):

        self.url_http_api = url_http_api
        self.url_image_host = url_image_host

        self.anidb = anidb
        self.id = id
        self._titles = []
        self._synonyms = []
        self._all_episodes = []
        self._episodes = {}
        self._picture = None
        self._rating_permanent = None
        self._rating_temporary = None
        self._rating_review = None
        self._categories = []
        self._tags = []
        self._start_date = None
        self._end_date = None
        self._description = None
        self._creators = []
        self._similareanimes = []
        self._url = None
        self._type = None
        self._episodecount = None
        self._characters = []
        self._xml = xml

        if xml:
            self.fill_from_xml(xml)

        self._loaded = False
        if auto_load:
            self.load()

    def __repr__(self):
        return "<Anime id: %s, loaded:%s>" % (self.id, self.loaded)

    @property
    def loaded(self):
        return self._loaded

    def load(self):
        """Load all extra information for this anime.

        The anidb url should look like this:
        http://api.anidb.net:9001/httpapi?request=anime&client={str}&clientver={int}&protover=1&aid={int}
        """
        params = {
            "client": self.anidb.client_name,
            "clientver": self.anidb.client_version,

            "protover": 1,
            "request": "anime",
            "aid": self.id
        }

        response = self.anidb.session.get(self.url_http_api, params=params)

        self._xml = ET.fromstring(str(response.content, encoding="utf-8"))
        self.fill_from_xml(self._xml)
        self._loaded = True

    def fill_from_xml(self, xml):
        if xml.find("titles") is not None:
            self._titles = [Title(self, n) for n in xml.find("titles")]
        else:
            self._titles = [Title(self, n) for n in xml.findall("title")]
            return
        self._synonyms = [t for t in self._titles if t.type == "synonym"]
        if xml.find("episodes") is not None:
            self._all_episodes = [Episode(self, n) for n in xml.find("episodes")]
            self._episodes = dict([
                (e.number, e) for e in self._all_episodes
                if e.type == 1
            ])
        if xml.find("picture") is not None:
            self._picture = Picture(self, xml.find("picture"), url_image_host=self.url_image_host)
        if xml.find("ratings") is not None:
            if xml.find("ratings").find("permanent") is not None:
                self._rating_permanent = xml.find("ratings").find("permanent").text
            if xml.find("ratings").find("temporary") is not None:
                self._rating_temporary = xml.find("ratings").find("temporary").text
            if xml.find("ratings").find("review") is not None:
                self._rating_review = xml.find("ratings").find("review").text
        if xml.find("categories") is not None:
            self._categories = [Category(self, c) for c in xml.find("categories")]
        if xml.find("tags") is not None:
            self._tags = [Tag(self, t) for t in xml.find("tags")]
        if xml.find("startdate") is not None:
            self._start_date = parse_date(xml.find("startdate").text)
        if xml.find("enddate") is not None:
            self._end_date = parse_date(xml.find("enddate").text)
        if xml.find("description") is not None:
            self._description = xml.find("description").text
        if xml.find("creators") is not None:
            self._creators = [Creator(self, c) for c in xml.find("creators")]
        if xml.find("similaranime") is not None:
            self._similareanimes = [Anime(self.anidb, int(c.attrib["id"]), auto_load=False) for c in xml.find("similaranime")]
        if xml.find("url") is not None:
            self._url = xml.find("url").text.strip()
        if xml.find("type") is not None:
            self._type = xml.find("type").text.strip()
        if xml.find("episodecount") is not None:
            self._episodecount = int(xml.find("episodecount").text.strip())
        if xml.find("characters") is not None:
            self._characters = [Character(self, c, self.url_image_host) for c in xml.find("characters")]
        if xml.find("tags") is not None:
            for tag in xml.find("tags"):
                self._tags.append(Tag(tag, xml))

    def get_title(self, type=None, lang=None):
        if not type:
            type = "main"
        for t in self._titles:
            if t.type == type:
                return t
        if not lang:
            lang = self.anidb.lang
        for t in self._titles:
            if t.lang == lang:
                return t

    @data_fetch
    def title(self):
        self.load()
        return self.get_title("main")

    @data_fetch
    def synonyms(self):
        return self._synonyms

    @data_fetch
    def episodes(self):
        return self._episodes

    @data_fetch
    def picture(self):
        return self._picture

    @data_fetch
    def rating_permanent(self):
        return self._rating_permanent

    @data_fetch
    def rating_temporary(self):
        return self._rating_temporary

    @data_fetch
    def rating_review(self):
        return self._rating_review

    @data_fetch
    def start_date(self):
        return self._start_date

    @data_fetch
    def end_date(self):
        return self._end_date

    @data_fetch
    def description(self):
        return self._description

    @data_fetch
    def titles(self):
        return self._titles

    @data_fetch
    def creators(self):
        return self._creators

    @data_fetch
    def similareanimes(self):
        return self._similareanimes

    @data_fetch
    def url(self):
        return self._url

    @data_fetch
    def type(self):
        return self._type

    @data_fetch
    def episodecount(self):
        return self._episodecount

    @data_fetch
    def characters(self):
        return self._characters

    @data_fetch
    def tags(self):
        return self._tags


class BaseAttribute(object):

    def __init__(self, anime, xml_node):
        self.anime = anime
        self._xml = xml_node

    def _attributes(self, *attrs):
        """Set the given attributes.

        :param list attrs: the attributes to be set.
        """
        for attr in attrs:
            setattr(self, attr, self._xml.attrib.get(attr))

    def _booleans(self, *attrs):
        """Set the given attributes after casting them to bools.

        :param list attrs: the attributes to be set.
        """
        for attr in attrs:
            value = self._xml.attrib.get(attr)
            setattr(self, attr, value is not None and value.lower() == "true")

    def _texts(self, *attrs):
        """Set the text values of the given attributes.

        :param list attrs: the attributes to be found.
        """
        for attr in attrs:
            value = self._xml.find(attr)
            setattr(self, attr, value.text if value is not None else None)

    def __str__(self):
        return self._xml.text

    def __repr__(self):
        return compat.u("<%s: %s>") % (
            self.__class__.__name__,
            str(self)
        )


class Category(BaseAttribute):

    def __init__(self, anime, xml_node):
        super(Category, self).__init__(anime, xml_node)
        self._attributes('id', 'weight')
        self._booleans('hentai')
        self._texts('name', 'description')

    def __str__(self):
        return self.name


class Character(BaseAttribute):
    def __init__(self, anime, xml_node, url_image_host=urls.URL_IMAGE_HOST):
        super(Character, self).__init__(anime, xml_node)
        self._attributes('id', 'type', 'update')
        if self.update:
            self.update = parse_date(self.update)

        self.name = None
        self.rating = None
        self.gender = None
        self.charactertype = None
        self.picture = None
        self.seiyuu = None
        self.description = None

        if xml_node.find("name") is not None:
            self.name = xml_node.find("name").text.strip()
        if xml_node.find("rating") is not None:
            self.rating = float(xml_node.find("rating").text)
        if xml_node.find("gender") is not None:
            self.gender = xml_node.find("gender").text.strip()
        if xml_node.find("charactertype") is not None:
            self.charactertype = CharacterType(self, xml_node.find("charactertype"))
        if xml_node.find("picture") is not None:
            self.picture = Picture(anime, xml_node.find("picture"), url_image_host)
        if xml_node.find("seiyuu") is not None:
            self.seiyuu = Seiyuu(anime, xml_node.find("seiyuu"))
        if xml_node.find("description") is not None:
            self.description = xml_node.find("description").text.strip()


class CharacterType:
    def __init__(self, character, xml_node):
        self.character = character
        self.id = int(xml_node.attrib.get("id"))
        self.name = xml_node.text.strip()


class Seiyuu(BaseAttribute):
    def __init__(self, anime, xml_node):
        super(Seiyuu, self).__init__(anime, xml_node)
        self._attributes('id', 'picture')
        self.name = xml_node.text.strip()


class Creator(BaseAttribute):
    def __init__(self, anime, xml_node):
        super(Creator, self).__init__(anime, xml_node)
        self._attributes('id', 'type')
        self.name = xml_node.text.strip()


class Tag(BaseAttribute):

    def __init__(self, anime, xml_node):
        super(Tag, self).__init__(anime, xml_node)
        self._attributes('id', 'update', 'weight')
        if self.update:
            self.update = parse_date(self.update)

        self._booleans('spoiler', 'localspoiler', 'globalspoiler', 'verified')
        self._texts('name', 'description')
        self.count = int(self.weight) if self.weight else 0
        """The importance of this tag."""

    def __cmp__(self, other):
        return self.count - other.count

    def __str__(self):
        return self.name


class Title(BaseAttribute):

    def __init__(self, anime, xml_node):
        super(Title, self).__init__(anime, xml_node)
        # apperently xml:lang is "{http://www.w3.org/XML/1998/namespace}lang"
        self.lang = self._xml.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
        self.type = self._xml.attrib.get("type")


class Picture(BaseAttribute):

    def __init__(self, anime, xml_node, url_image_host=urls.URL_IMAGE_HOST):
        super().__init__(anime, xml_node)
        self.url_image_host = url_image_host if url_image_host.endswith("/") else url_image_host + "/"

    def __str__(self):
        return self.url

    @property
    def url(self):
        return self.url_image_host + ("%s" % self._xml.text)

    @property
    def path(self):
        file = os.path.join(self.anime.anidb.cache_path, self._xml.text)

        if os.path.exists(file):
            modified_date = datetime.fromtimestamp(os.path.getmtime(file))
            if modified_date + timedelta(1) > datetime.now():
                return file
        return download_file(file, self.url)


class Episode(BaseAttribute):

    def __init__(self, anime, xml_node):
        super(Episode, self).__init__(anime, xml_node)
        self._attributes('id')
        self._texts('airdate', 'length', 'epno')
        self.airdate = parse_date(self.airdate)

        self.titles = [Title(self, n) for n in self._xml.findall("title")]
        self.type = int(self._xml.find("epno").attrib["type"])
        self.number = self.epno or 0
        if self.type == 1:
            self.number = int(self.number)

    @property
    def title(self):
        return self.get_title()

    def get_title(self, lang=None):
        if not lang:
            lang = self.anime.anidb.lang
        for t in self.titles:
            if t.lang == lang:
                return t

    def __str__(self):
        return compat.u("%s: %s") % (self.number, self.title)

    def __cmp__(self, other):
        if self.type > other.type:
            return -1
        elif self.type < other.type:
            return 1

        if self.number < other.number:
            return -1
        return 1
