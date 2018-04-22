from abc import abstractmethod


class BaseParser:
    """
    This is the base class for Parsers
    it defines the interface for a parser
    """
    @abstractmethod
    def __init__(self, file, callback=None):
        """
        Initializes the parser

        :param file: path to file
        :param callback: callback is called with element
        """
        pass

    @abstractmethod
    def parse(self):
        """
        Start the parsing process
        """
        pass
