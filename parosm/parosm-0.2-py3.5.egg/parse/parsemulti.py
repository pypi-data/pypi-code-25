import os.path
import magic

from parosm.parse.parsebase import BaseParser
from parosm.parse.parsepbf import PBFParser
from parosm.parse.parsexml import XMLParser


class MultiParser(BaseParser):
    def __init__(self, file, callback=None):
        super().__init__(file, callback)
        self.__file = file
        if not os.path.isfile(file):
            raise Exception('is not a file')

        self.__callback = self.__default_callback \
            if callback is None else callback

        file_type = magic.from_file(file)
        if file_type == 'OpenStreetMap XML data':
            self.__parser = XMLParser(self.__file,
                                      self.__callback)
        elif file_type == 'OpenStreetMap Protocolbuffer Binary Format':
            self.__parser = PBFParser(self.__file,
                                      self.__callback)
        else:
            raise Exception('Not a osm file')

    @staticmethod
    def __default_callback(element):
        print(str(element))

    def parse(self):
        self.__parser.parse()
