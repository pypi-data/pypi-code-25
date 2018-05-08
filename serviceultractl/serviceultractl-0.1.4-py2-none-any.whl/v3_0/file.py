# -*- coding: utf-8 -*-
from .file_ch import File as File_ch
from .file_en import File as File_en
from .file_json import File as File_json
from .base.file import File as File_base


class FileDispatch(object):
    @staticmethod
    def list(auth, path, format_json):
        if format_json:
            File_json.list(auth, path)
        else:
            if auth.language == "en":
                File_en.list(auth, path)
            else:
                File_ch.list(auth, path)

    @staticmethod
    def upload(auth, dest, files):
        File_base._upload(auth, dest, files)

    @staticmethod
    def download(auth, path):
        File_base._download(auth, path)