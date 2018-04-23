# coding: utf-8

import os

from gensim.models.doc2vec import Doc2Vec

from flask import abort
from flask import send_file
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful.inputs import boolean

from mlang.nlp import get_tokenize

from mlang.config import SERVICE_D2V_DIR

from mlang.semantic.representation import D2VTextRepresentation

from mlang.utils import get_cache, put_cache

from mlang.semantic.d2v import load as load_d2v
from mlang.semantic.d2v import train as train_d2v
from mlang.semantic.d2v import DEFAULT_D2V_MODEL_FILE

from mlang_server.service.vocab import get_vocab
from mlang_server.service.vocab import DEFAULT_VOCAB

from mlang_server.service.corpus import get_corpus


def init(api, furl):
    api.add_resource(D2v, furl('/d2v/<d2vid>'))
    api.add_resource(D2vMetaData, furl('/d2v/info/<d2vid>'))
    api.add_resource(D2vMetaDataList, furl('/d2v/list'))


DEFAULT_D2V = 'defaultd2v'


def d2v_path(d2vid):
    return os.path.join(SERVICE_D2V_DIR, d2vid)


def get_doc2vec(d2vid, update_cache):
    """
    从缓存中获取 W2VTextRepresentation，没有则从d2vid文件里载入
    :param d2vid:
    :param update_cache:
    :rtype: Doc2Vec
    :return: Doc2Vec
    """
    d2v_model = get_cache(d2vid)

    if update_cache:
        d2v_model = None

    if d2v_model is None:
        if d2vid == DEFAULT_D2V:
            d2v_file = DEFAULT_D2V_MODEL_FILE
        else:
            d2v_file = d2v_path(d2vid)
        d2v_model = load_d2v(d2v_file)
        put_cache(d2vid, d2v_model)

    return d2v_model


def get_self_tokenize(impl, dictionary=None, max_len=None):
    return get_tokenize(impl, dictionary=dictionary, max_len=max_len)


class D2v(Resource):
    """
    doc2vec 模型
    """
    def post(self, d2vid):
        rqp = reqparse.RequestParser()

        rqp.add_argument('corpusid', type=str, required=True, help='corpus id')
        rqp.add_argument('tokenize', type=str, required=False, default='ltp', help='tokenize method, [ltp/jieba/fmm/rmm], fmm/rmm -> vocabid + max_len')
        rqp.add_argument('vocabid', type=str, required=False, help='vocabid: token vocab id', default=DEFAULT_VOCAB)
        rqp.add_argument('max_len', type=int, required=False, default=4, help='max_len: max word length')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update_cache')

        # doc2vec model args
        rqp.add_argument('size', type=int, required=False, default=100, help='doc2vec model args size')
        rqp.add_argument('dm', type=int, required=False, default=1, help='doc2vec model args dm')
        rqp.add_argument('dm_mean', type=int, required=False, default=1, help='doc2vec model args dm_mean')
        rqp.add_argument('epochs', type=int, required=False, default=5, help='doc2vec model args epochs')
        rqp.add_argument('window', type=int, required=False, default=5, help='doc2vec model args window')
        rqp.add_argument('alpha', type=float, required=False, default=0.025, help='doc2vec model args alpha')
        rqp.add_argument('min_count', type=int, required=False, default=5, help='doc2vec model args min_count')
        rqp.add_argument('max_vocab_size', type=int, required=False, help='doc2vec model args max_vocab_size')
        rqp.add_argument('workers', type=int, required=False, default=3, help='doc2vec model args workers')
        rqp.add_argument('hs', type=int, required=False, default=0, help='doc2vec model args hs')
        rqp.add_argument('negative', type=int, required=False, default=5, help='doc2vec model args negative')
        rqp.add_argument('compute_loss', type=boolean, required=False, default=False, help='doc2vec model args compute_loss')

        args = rqp.parse_args()

        corpusid = args['corpusid']
        tokenize_impl = args['tokenize']
        vocabid = args['vocabid']
        max_len = args['max_len']
        update_cache = args['update_cache']

        model_args = {
            'size': args['size'],
            'dm': args['dm'],
            'dm_mean': args['dm_mean'],
            'epochs': args['epochs'],
            'window': args['window'],
            'alpha': args['alpha'],
            'min_count': args['min_count'],
            'max_vocab_size': args['max_vocab_size'],
            'workers': args['workers'],
            'hs': args['hs'],
            'negative': args['negative'],
            'compute_loss': args['compute_loss']

        }

        vocab = get_vocab(vocabid, update_cache)
        tokenize = get_tokenize(tokenize_impl, dictionary=vocab, max_len=max_len)
        corpus = get_corpus(corpusid)
        train_d2v(corpus, d2v_path(d2vid), tokenize=tokenize, **model_args)
        return 'success'

    def delete(self, d2vid):
        file_path = d2v_path(d2vid)
        if os.path.exists(file_path):
            os.remove(file_path)
        return 'success'

    def get(self, d2vid):
        file_path = d2v_path(d2vid)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            abort(404)


class D2vMetaData(Resource):
    """
    Word2vec模型信息
    """
    def get(self, d2vid):
        file_path = d2v_path(d2vid)
        if os.path.exists(file_path):
            return {
                'size': int(os.path.getsize(file_path)),
                'atime': int(os.path.getatime(file_path)),
                'ctime': int(os.path.getctime(file_path)),
                'mtime': int(os.path.getmtime(file_path))
            }
        else:
            return {}


class D2vMetaDataList(Resource):
    """语料文件信息"""

    def get(self):
        files = []

        for f in os.listdir(SERVICE_D2V_DIR):
            file = os.path.join(SERVICE_D2V_DIR, f)
            if not os.path.isfile(file):
                continue
            files.append({
                'd2vid': f,
                'size': int(os.path.getsize(file)),
                'atime': int(os.path.getatime(file)),
                'ctime': int(os.path.getctime(file)),
                'mtime': int(os.path.getmtime(file))
            })

        return files
