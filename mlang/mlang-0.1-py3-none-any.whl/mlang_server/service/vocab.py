# coding: utf-8

import os

from flask import abort
from flask import send_file
from flask_restful import reqparse
from flask_restful import Resource

from werkzeug.datastructures import FileStorage

from mlang.nlp import build_vocab

from mlang.utils import iter_file
from mlang.utils import get_cache
from mlang.utils import put_cache

from mlang.res.vocab import Vocab
from mlang.res.vocab import DefaultVocab
from mlang.res.vocab import DefaultDegreeVocab
from mlang.res.vocab import DefaultNegatorVocab
from mlang.res.vocab import DefaultStopWordVocab
from mlang.res.vocab import DefaultSentimentVocab

from mlang.config import SERVICE_VOCAB_DIR

from mlang_server.service.corpus import corpus_exists
from mlang_server.service.corpus import get_corpus


def init(api, furl):
    api.add_resource(VVocab, furl('/vocab/<vocabid>'))
    api.add_resource(VVocabUpload, furl('/vocab/upload/<vocabid>'))
    api.add_resource(VocabMetaData, furl('/vocab_info/<vocabid>'))
    api.add_resource(VocabMetaDataList, furl('/vocab_list'))


def vocab_path(vocabid):
    return os.path.join(SERVICE_VOCAB_DIR, vocabid)


def vocab_exists(vocabid):
    return os.path.exists(vocab_path(vocabid))


DEFAULT_VOCAB = 'defaultvocab'
DEFAULT_VOCAB_STOP = 'defaultstopwordvocab'
DEFAULT_VOCAB_DEGREE = 'defaultdegreevocab'
DEFAULT_VOCAB_NEGATOR = 'defaultnegatorvocab'
DEFAULT_VOCAB_SENTIMENT = 'defaultsentimentvocab'


def get_vocab(vocabid, update_cache):
    """
    从缓存中获取Vocab，缓存中没有则从文件中构建
    :param vocabid:
    :param update_cache:
    :rtype: Vocab
    """
    vocab = get_cache(vocabid)

    if update_cache:
        vocab = None

    if vocab is None:
        if vocabid == DEFAULT_VOCAB:
            vocab = DefaultVocab.get()
        elif vocabid == DEFAULT_VOCAB_STOP:
            vocab = DefaultStopWordVocab.get()
        elif vocabid == DEFAULT_VOCAB_DEGREE:
            vocab = DefaultDegreeVocab.get()
        elif vocabid == DEFAULT_VOCAB_NEGATOR:
            vocab = DefaultNegatorVocab.get()
        elif vocabid == DEFAULT_VOCAB_SENTIMENT:
            vocab = DefaultSentimentVocab.get()
        else:
            vocab = Vocab(vocab_file=vocab_path(vocabid))

        put_cache(vocabid, vocab)

    return vocab


class VVocab(Resource):
    """
    构建词表接口
    """
    def post(self, vocabid):
        """"
        使用语料构建词表
        """
        rqp = reqparse.RequestParser()
        rqp.add_argument('corpusid', required=True, type=str, trim=True, help='param [corpusid] is required!')
        rqp.add_argument('impl', required=False, type=str, trim=True, default='ltp', help='impl: [ltp/jieba/full/fast]')
        rqp.add_argument('min_freq', required=False, type=int, default=5, help='min_freq')
        rqp.add_argument('topn', required=False, type=int, default=10000, help='topn')
        args = rqp.parse_args()

        corpusid = args['corpusid']
        impl = args['impl']
        topn = args['topn']
        min_freq = args['min_freq']

        if not corpus_exists(corpusid):
            abort(500)

        corpus = get_corpus(corpusid)

        vocab = build_vocab(corpus, impl=impl, topn=topn, min_freq=min_freq)
        if vocab is not None:
            vocab.write_vocab_file(vocab_path(vocabid))
            return 'success'
        else:
            return 'fail'

    def get(self, vocabid):
        """
        下载词表
        :param vocabid:
        :return:
        """
        file_path = vocab_path(vocabid)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            abort(404)

    def delete(self, vocabid):
        """"
        删除词表
        """
        file_path = vocab_path(vocabid)
        if os.path.exists(file_path):
            os.remove(file_path)
        return 'ok'


class VVocabUpload(Resource):
    """
    词表上传
    """
    def post(self, vocabid):
        parser = reqparse.RequestParser()
        parser.add_argument('vocab', required=True, type=FileStorage, help='param [vocab] is required', location='files')
        parser.add_argument('action', required=False, type=str, default='overwrite', help='param [action] overwrite/append is required!')

        args = parser.parse_args()
        file = args['vocab']
        op = args['action']

        mode = 'ab' if op == 'append' else 'wb'
        with open(vocab_path(vocabid), mode) as f:
            file.save(f)

        return 'ok'


class VocabMetaData(Resource):
    """
    词表文件信息
    """
    def get(self, vocabid):
        """
        获取词表信息
        :param vocabid:
        :return:
        """
        file_path = vocab_path(vocabid)
        if os.path.exists(file_path):

            c = 0
            for _ in iter_file(vocab_path(vocabid)):
                c += 1

            return {
                'vsize': c,
                'size': int(os.path.getsize(file_path)),
                'atime': int(os.path.getatime(file_path)),
                'ctime': int(os.path.getctime(file_path)),
                'mtime': int(os.path.getmtime(file_path))
            }
        else:
            return {}


class VocabMetaDataList(Resource):
    """词表文件信息"""
    def get(self):
        """
        获取词表列表信息
        :return:
        """
        files = []

        for f in os.listdir(SERVICE_VOCAB_DIR):
            file = os.path.join(SERVICE_VOCAB_DIR, f)
            if not os.path.isfile(file):
                continue

            c = 0
            for _ in iter_file(file):
                c += 1

            files.append({
                'vocabid': f,
                'vsize': c,
                'size': int(os.path.getsize(file)),
                'atime': int(os.path.getatime(file)),
                'ctime': int(os.path.getctime(file)),
                'mtime': int(os.path.getmtime(file))
            })

        return files
