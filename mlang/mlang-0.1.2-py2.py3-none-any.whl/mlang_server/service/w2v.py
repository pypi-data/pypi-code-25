# coding: utf-8

import os

from flask import abort
from flask import send_file
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful.inputs import boolean

from mlang.nlp import get_tokenize

from mlang.config import SERVICE_W2V_DIR

from mlang.utils import get_cache, put_cache

from mlang.semantic.w2v import load as load_w2v
from mlang.semantic.w2v import train as train_w2v
from mlang.semantic.w2v import DEFAULT_W2V_MODEL_FILE

from mlang_server.service.vocab import get_vocab
from mlang_server.service.vocab import DEFAULT_VOCAB

from mlang_server.service.corpus import get_corpus


def init(api, furl):
    api.add_resource(W2v, furl('/w2v/<w2vid>'))
    api.add_resource(W2vMetaData, furl('/w2v/info/<w2vid>'))
    api.add_resource(W2vMetaDataList, furl('/w2v/list'))


DEFAULT_W2V = 'defaultw2v'


def w2v_path(w2vid):
    return os.path.join(SERVICE_W2V_DIR, w2vid)


def get_word2vec(w2vid, update_cache):
    """
    从缓存中获取W2VWordRepresentation，没有则从w2vid文件里载入
    :param w2vid:
    :param update_cache:
    :rtype: Word2VecKeyedVectors
    :return:
    """
    w2v_model = get_cache(w2vid)

    if update_cache:
        w2v_model = None

    if w2v_model is None:
        if w2vid == DEFAULT_W2V:
            binary_file = DEFAULT_W2V_MODEL_FILE
        else:
            binary_file = w2v_path(w2vid)
        w2v_model = load_w2v(binary_file)
        put_cache(w2vid, w2v_model)

    return w2v_model


class W2v(Resource):
    """
    word2vec模型
    """
    def post(self, w2vid):
        rqp = reqparse.RequestParser()

        rqp.add_argument('corpusid', type=str, required=True, help='corpus id')
        rqp.add_argument('tokenize', type=str, required=False, default='ltp', help='tokenize method, [ltp/jieba/fmm/rmm], fmm/rmm -> vocabid + max_len')
        rqp.add_argument('vocabid', type=str, required=False, help='vocabid: token vocab id', default=DEFAULT_VOCAB)
        rqp.add_argument('max_len', type=int, required=False, default=4, help='max_len: max word length')
        rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update_cache')

        # word2vec model args
        rqp.add_argument('size', type=int, required=False, default=100, help='word2vec model args size')
        rqp.add_argument('epochs', type=int, required=False, default=5, help='word2vec model args epochs')
        rqp.add_argument('window', type=int, required=False, default=5, help='word2vec model args window')
        rqp.add_argument('alpha', type=float, required=False, default=0.025, help='word2vec model args alpha')
        rqp.add_argument('min_count', type=int, required=False, default=5, help='word2vec model args min_count')
        rqp.add_argument('max_vocab_size', type=int, required=False, help='word2vec model args max_vocab_size')
        rqp.add_argument('workers', type=int, required=False, default=3, help='word2vec model args workers')
        rqp.add_argument('sg', type=int, required=False, default=0, help='word2vec model args sg')
        rqp.add_argument('hs', type=int, required=False, default=0, help='word2vec model args hs')
        rqp.add_argument('negative', type=int, required=False, default=5, help='word2vec model args negative')
        rqp.add_argument('cbow_mean', type=int, required=False, default=1, help='word2vec model args cbow_mean')
        rqp.add_argument('compute_loss', type=boolean, required=False, default=False, help='word2vec model args compute_loss')

        args = rqp.parse_args()

        corpusid = args['corpusid']
        tokenize_impl = args['tokenize']
        vocabid = args['vocabid']
        max_len = args['max_len']
        update_cache = args['update_cache']

        model_args = {
            'size': args['size'],
            'epochs': args['epochs'],
            'window': args['window'],
            'alpha': args['alpha'],
            'min_count': args['min_count'],
            'max_vocab_size': args['max_vocab_size'],
            'workers': args['workers'],
            'sg': args['sg'],
            'hs': args['hs'],
            'negative': args['negative'],
            'cbow_mean': args['cbow_mean'],
            'compute_loss': args['compute_loss']

        }

        vocab = get_vocab(vocabid, update_cache)
        tokenize = get_tokenize(tokenize_impl, dictionary=vocab, max_len=max_len)
        corpus = get_corpus(corpusid)
        train_w2v(corpus, w2v_path(w2vid), tokenize=tokenize, **model_args)
        return 'success'

    def delete(self, w2vid):
        file_path = w2v_path(w2vid)
        if os.path.exists(file_path):
            os.remove(file_path)
        return 'success'

    def get(self, w2vid):
        file_path = w2v_path(w2vid)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            abort(404)


class W2vMetaData(Resource):
    """
    Word2vec模型信息
    """
    def get(self, w2vid):
        file_path = w2v_path(w2vid)
        if os.path.exists(file_path):
            return {
                'size': int(os.path.getsize(file_path)),
                'atime': int(os.path.getatime(file_path)),
                'ctime': int(os.path.getctime(file_path)),
                'mtime': int(os.path.getmtime(file_path))
            }
        else:
            return {}


class W2vMetaDataList(Resource):
    """语料文件信息"""

    def get(self):
        files = []

        for f in os.listdir(SERVICE_W2V_DIR):
            file = os.path.join(SERVICE_W2V_DIR, f)
            if not os.path.isfile(file):
                continue
            files.append({
                'w2vid': f,
                'size': int(os.path.getsize(file)),
                'atime': int(os.path.getatime(file)),
                'ctime': int(os.path.getctime(file)),
                'mtime': int(os.path.getmtime(file))
            })

        return files
