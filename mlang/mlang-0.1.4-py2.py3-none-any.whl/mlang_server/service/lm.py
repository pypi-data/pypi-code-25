# coding: utf-8

import os
import codecs

from flask import abort
from flask import send_file
from flask_restful import reqparse
from flask_restful import Resource

from flask_restful.inputs import boolean

from mlang.nlp import Token
from mlang.nlp import get_tokenize
from mlang.res.corpus import Corpus

from mlang.model.lm import BerkeleyLM

from mlang.config import SERVICE_LM_DIR, DEFAULT_VOCAB
from mlang.config import SERVICE_TMP_DIR

from mlang.utils import get_cache
from mlang.utils import put_cache

from mlang_server.service.vocab import get_vocab
from mlang_server.service.corpus import get_corpus


DEFAULT_LM = 'mobile.binary'


def init(api, furl):
    api.add_resource(LM, furl('/lm/<lmid>'))
    api.add_resource(LmMetaData, furl('/lm_info/<lmid>'))
    api.add_resource(LmMetaDataList, furl('/lm_list'))
    api.add_resource(LMProb, furl('/lm/prob'))


def lm_exists(lmid):
    return os.path.exists(os.path.join(SERVICE_LM_DIR, lmid))


def lm_path(lmid):
    return os.path.join(SERVICE_LM_DIR, lmid)


def get_lm(lmid, update_cache):
    """
    :rtype: BerkeleyLM
    """
    lm = get_cache(lmid)

    if update_cache:
        lm = None

    if lm is None:
        lm = BerkeleyLM(lm_bin_file=lm_path(lmid))
        put_cache(lmid, lm)

    return lm


class LM(Resource):
    """
    语言模型
    """

    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('corpusid', type=str, required=True, help='corpusid')
        self.rqp.add_argument('order', type=int, required=False, default=3, help='n-gram order')
        self.rqp.add_argument('tokenize', type=str, required=False, default=None, help='tokenize method, [ltp/jieba/fmm/rmm], fmm/rmm -> vocabid + max_len')
        self.rqp.add_argument('vocabid', type=str, required=False, help='vocabid: token vocab id', default=DEFAULT_VOCAB)
        self.rqp.add_argument('max_len', type=int, required=False, default=4, help='max_len: max word length')
        self.rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update_cache')

    def post(self, lmid):
        args = self.rqp.parse_args()
        corpusid = args['corpusid']

        tokenize_impl = args['tokenize']
        vocabid = args['vocabid']
        max_len = args['max_len']

        update_cache = args['update_cache']

        # 设置分词逻辑，默认是一个字一个词
        if tokenize_impl:
            vocab = get_vocab(vocabid, update_cache)
            tokenize = get_tokenize(tokenize_impl, dictionary=vocab, max_len=max_len)
        else:
            tokenize = lambda line: [Token(0, t) for t in line]

        def record_reader(line, **kwargs):
            return ' '.join([t.word for t in tokenize(line)])

        corpus = get_corpus(corpusid)
        corpus = Corpus(corpus, record_reader=record_reader)

        # 将分词后的语料保存到临时文件夹
        # tokenize corpus
        tmp_file = os.path.join(SERVICE_TMP_DIR, '%s.tmp.txt' % corpusid)
        with codecs.open(tmp_file, encoding='utf-8', mode='w') as f:
            for line in corpus:
                f.write('%s\n' % line)

        # 训练语言模型
        order = args['order']
        BerkeleyLM.train(order, tmp_file, lm_path(lmid))

        return 'success'

    def delete(self, lmid):
        if lm_exists(lmid):
            os.remove(lm_path(lmid))

        return 'success'

    def get(self, lmid):
        if lm_exists(lmid):
            return send_file(lm_path(lmid))
        else:
            abort(404)


class LMProb(Resource):
    """
    使用语言模型计算你句子概率
    """
    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('txt', type=str, required=True, help='txt')
        self.rqp.add_argument('lmid', type=str, required=False, default=DEFAULT_LM, help='lmid')
        self.rqp.add_argument('tokenize', type=str, required=False, help='tokenize method, [ltp/jieba/fmm/rmm], fmm/rmm -> vocabid + max_len')
        self.rqp.add_argument('vocabid', type=str, required=False, help='vocabid: token vocab id',
                              default=DEFAULT_VOCAB)
        self.rqp.add_argument('max_len', type=int, required=False, default=4, help='max_len: max word length')
        self.rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update_cache')

    def post(self):
        args = self.rqp.parse_args()

        txt = args['txt']
        lmid = args['lmid']

        update_cache = args['update_cache']

        tokenize_impl = args['tokenize']
        if tokenize_impl is None:
            words = [t for t in txt]
        else:
            vocabid = args['vocabid']
            max_len = args['max_len']

            vocab = get_vocab(vocabid, update_cache)
            tokenize = get_tokenize(tokenize_impl, dictionary=vocab, max_len=max_len)
            words = [t.word for t in tokenize(txt)]

        lm = get_lm(lmid, update_cache)
        return lm.sentence_prob(words)


class LmMetaData(Resource):
    """
    语言模型文件信息
    """
    def get(self, lmid):
        if lm_exists(lmid):
            file_path = lm_path(lmid)
            return {
                'size': int(os.path.getsize(file_path)),
                'atime': int(os.path.getatime(file_path)),
                'ctime': int(os.path.getctime(file_path)),
                'mtime': int(os.path.getmtime(file_path))
            }
        else:
            return {}


class LmMetaDataList(Resource):
    """
    语言模型文件信息
    """
    def get(self):
        files = []

        for f in os.listdir(SERVICE_LM_DIR):
            file = os.path.join(SERVICE_LM_DIR, f)
            if not os.path.isfile(file):
                continue
            files.append({
                'lmid': f,
                'size': int(os.path.getsize(file)),
                'atime': int(os.path.getatime(file)),
                'ctime': int(os.path.getctime(file)),
                'mtime': int(os.path.getmtime(file))
            })

        return files
