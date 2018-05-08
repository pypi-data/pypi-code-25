# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.file import FileDispatch as File


class UploadCommands(object):
    @args("--dest", dest="dest", default="/", help="")
    @args("--files", dest="files", required=True, nargs="+", help="")
    def file(self, auth, dest, files):
        """upload file"""
        File.upload(auth, dest, files)
