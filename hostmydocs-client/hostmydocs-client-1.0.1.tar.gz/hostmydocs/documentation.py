#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging
import os.path


class Documentation:
    """
    This class is a representation of a documentation you want to host (or already hosted)
    on HostMyDocs server
    """

    def __init__(self, name: str, language: str, version: str, zip_archive_path=None):
        """

        :param name: The name of the documented project
        :param zip_archive_path: Path to the zip which contain the documentation in right format for HostMyDocs. If None means the doc is present on HostMyDocs server
        :param language: The language of your documentation (can be a programing language or English, French, etc...)
        :param version: The version of your documentation
        """

        self.name = name
        self.version = version
        self.language = language
        self.zip_archive_path = zip_archive_path

    def is_local_documentation(self) -> bool:
        """

        :return: True if the documentation is local and can be uploaded to HostMyDocs server
        """

        if self.zip_archive_path is None:
            logging.debug("zip_archive_path is None")
            return False

        if os.path.exists(self.zip_archive_path) is False:
            logging.debug("zip_archive_path is not present: {}".format(self.zip_archive_path))
            return False

        return True

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version and self.language == other.language
