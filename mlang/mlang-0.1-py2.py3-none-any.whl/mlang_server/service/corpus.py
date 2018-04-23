# coding: utf-8

import os

from flask import abort
from flask import send_file
from flask_restful import Resource
from flask_restful import reqparse

from werkzeug.datastructures import FileStorage

from mlang.res.corpus import FileCorpus

from mlang.config import SERVICE_CORPUS_DIR


def init(api, furl):
    """service入口"""
    api.add_resource(Corpus, furl('/corpus/<corpusid>'))
    api.add_resource(CorpusMetaData, furl('/corpus_info/<corpusid>'))
    api.add_resource(CorpusMetaDataList, furl('/corpus_list'))


def corpus_path(corpusid):
    return os.path.join(SERVICE_CORPUS_DIR, corpusid)


def corpus_exists(corpusid):
    """
    :param corpusid:
    :return:
    :rtype: bool
    """
    return os.path.exists(corpus_path(corpusid))


def get_corpus(corpusid):
    """
    :param corpusid:
    :return:
    :rtype: FileCorpus
    """
    return FileCorpus(corpus_path(corpusid))


class Corpus(Resource):
    """
    文件上传接口
    """
    def post(self, corpusid):
        parser = reqparse.RequestParser()
        parser.add_argument('corpus', required=True, type=FileStorage, help='param [file] is required', location='files')
        parser.add_argument('action', required=True, type=str, help='param [action] overwrite/append is required!')

        args = parser.parse_args()
        file = args['corpus']
        op = args['action']

        mode = 'ab' if op == 'append' else 'wb'
        with open(corpus_path(corpusid), mode) as f:
            file.save(f)

        return 'ok'

    def delete(self, corpusid):
        file_path = corpus_path(corpusid)
        if os.path.exists(file_path):
            os.remove(file_path)
        return 'ok'

    def get(self, corpusid):
        file_path = corpus_path(corpusid)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            abort(404)


class CorpusMetaData(Resource):
    """
    语料文件信息
    """
    def get(self, corpusid):
        file_path = corpus_path(corpusid)
        if os.path.exists(file_path):
            return {
                'size': int(os.path.getsize(file_path)),
                'atime': int(os.path.getatime(file_path)),
                'ctime': int(os.path.getctime(file_path)),
                'mtime': int(os.path.getmtime(file_path))
            }
        else:
            return {}


class CorpusMetaDataList(Resource):
    """语料文件信息"""

    def get(self):
        files = []

        for f in os.listdir(SERVICE_CORPUS_DIR):
            file = os.path.join(SERVICE_CORPUS_DIR, f)
            if not os.path.isfile(file):
                continue
            files.append({
                'corpusid': f,
                'size': int(os.path.getsize(file)),
                'atime': int(os.path.getatime(file)),
                'ctime': int(os.path.getctime(file)),
                'mtime': int(os.path.getmtime(file))
            })

        return files
